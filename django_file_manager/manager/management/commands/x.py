from django.core.management import BaseCommand
from manager.models import Peer, Transactions

__author__ = 'amber'


class Command(BaseCommand):

    def handle(self, *args, **options):
        x = Peer.objects.latest('id')
        x.mine_block('first', 'agdfelksuygdflsergflserfglhsebrlgfvsZDgfvsDfzsfcSZfvdszegdfv')
        print(x)
