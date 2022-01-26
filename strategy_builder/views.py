from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from strategy_builder.models import Node, Strategy, StrategyTicker
from entities.strategy_builder import TreeNodeValidator
from threading import Thread
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from strategy_builder.serializers import StrategySerializer
from rest_framework.request import Request
# Create your views here.


class StrategyList(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = StrategySerializer

    def get_queryset(self):
        if self.request.query_params.get('enabled') == '1':
            return self.request.user.strategy_list.filter(enabled=True)

        return self.request.user.strategy_list.all()


class CreateStrategy(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request: Request) -> Response:
        token_map = {}
        for instrument in request.user.userprofile.kite.instruments():
            token_map[instrument['tradingsymbol']] = instrument

        exit_tree = TreeNodeValidator.from_dict(request.data['exit']['root'])
        entry_tree = TreeNodeValidator.from_dict(request.data['entry']['root'])

        if not(TreeNodeValidator.is_complete_binary_tree(entry_tree)):
            raise APIException("invalid entry exception",
                               status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not(TreeNodeValidator.is_complete_binary_tree(exit_tree)):
            raise APIException("invalid exit expression",
                               status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            strategy = Strategy(
                name=request.data['name'],
                lot_size=request.data['lot_size'],
                loss_percent=request.data['loss_percent'],
                profit_percent=request.data['profit_percent'],
                user=request.user,
            )
            strategy.save()

            tickers = request.data['tickers']
            for _ticker in tickers:
                exchange, ticker = _ticker.strip().split(':')
                StrategyTicker.objects.create(
                    ticker=ticker,
                    exchange=exchange,
                    strategy=strategy,
                    instrument_token=token_map[ticker]['instrument_token'],
                    lot_size=token_map[ticker]['lot_size']
                )

        except Exception as e:
            strategy.delete()

            raise APIException(
                str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if request.data['entry']['root'] and request.data['exit']['root']:
            entry_node = Node.from_dict(request.data['entry']['root'])
            exit_node = Node.from_dict(request.data['exit']['root'])

            strategy.entry_node = entry_node
            strategy.exit_node = exit_node

            strategy.save()

            response_status = status.HTTP_201_CREATED
            response_message = {'message': 'created strategy successfully'}
        else:
            strategy.delete()

            raise APIException('unable to create strategy',
                               code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response_message, status=response_status)


class ToggleStrategy(APIView):
    permission_classes = [IsAuthenticated, ]

    def patch(self, request, pk):
        try:
            strategy = request.user.strategy_list.get(pk=pk)
        except Exception:
            raise APIException(
                f"strategy with id {pk} not found for the user", code=status.HTTP_404_NOT_FOUND)

        strategy.enabled = not(strategy.enabled)
        strategy.save()

        return Response({
            "message": "strategy updated successfully",
        }, status=status.HTTP_200_OK)


class DeleteStrategy(APIView):
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, pk):
        try:
            strategy = request.user.strategy_list.get(pk=pk)

            strategy.entry_node.delete()
            strategy.exit_node.delete()
        except Exception:
            raise APIException(
                f"failed to delete strategy with id {pk}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
