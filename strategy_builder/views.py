from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import APIException
from strategy_builder.models import Node, Strategy, StrategyTicker
from entities.strategy_builder import TreeNodeValidator

# Create your views here.


class CreateStrategy(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request: Request) -> Response:
        exit_tree = TreeNodeValidator.from_dict(data['exit']['root'])
        entry_tree = TreeNodeValidator.from_dict(data['entry']['root'])

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
                user=request.user
            )
            strategy.save()

            tickers = request.data['tickers'].split(',')

            for _ticker in tickers:
                exchange, ticker = _ticker.strip().split(':')
                StrategyTicker.objects.create(
                    ticker=ticker,
                    exchange=exchange,
                    strategy=strategy,
                )

        except Exception as e:
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
            raise APIException('unable to create strategy',
                               code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response_message, status=response_status)
