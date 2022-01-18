from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from strategy_builder.models import Node, Strategy, StrategyTicker


# Create your views here.
class CreateStrategy(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request: Request) -> Response:
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
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if request.data['entry']['root'] and request.data['exit']['root']:
            entry_node = Node.from_dict(request.data['entry']['root'])
            exit_node = Node.from_dict(request.data['exit']['root'])

            strategy.entry_node = entry_node
            strategy.exit_node = exit_node

            strategy.save()

            response_status = status.HTTP_201_CREATED
            response_message = {'message': 'created strategy successfully'}
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_message = {'message': 'unable to create strategy'}

        return Response(response_message, status=response_status)
