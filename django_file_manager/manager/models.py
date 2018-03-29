from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
from hashlib import sha256
import datetime
import logging
import pytz
from django.urls import reverse
from .utils import SymmetricEncryption, JsonApi, EncryptionApi
#import magic
#from validatedfile import ValidatedFileField

class User(AbstractUser):
    is_subscriber = models.BooleanField(default=False)
    is_publisher = models.BooleanField(default=False)


class Subject(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.name



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Document(models.Model):
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='document_publisher')
    #subscriber = models.ManyToManyField(Subscriber, through='SubFile')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, related_name='document_subject')
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/%Y/%m/%d')
 #   document = ValidatedFileField(null=True, blank=True, uploaded_to='documents/%Y/%m/%d', max_uploaded_size=10240, content_types=['application/pdf', 'image/png'])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #history = models.ForeignKey(History, on_delete=models.CASCADE, null=True, related_name='document_history')

    def __str__(self):
        return self.document.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    documents = models.ManyToManyField(Document)
    interests = models.ManyToManyField(Subject, related_name='interested_students')


    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username


class TakenQuiz(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class SubFile(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='sub_files')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='sub_files')
    date = models.DateTimeField(auto_now_add=True)


class History(models.Model):
#    v = 'R'
 #   e = 'W'
    OPERATION_OPTIONS = (('c', 'Create'), ('m', 'Modify'), ('s', 'Subscribe'))
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='file_history')
    operation = models.CharField(max_length=10, choices=OPERATION_OPTIONS, default='c')
    date = models.DateTimeField(auto_now_add=True)
    performer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_performer')
    #sub_count = models.IntegerField(default=0)


class SubscribeAnswer(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')

class Transactions(models.Model):
    sender = models.CharField(max_length=200)
    receiver = models.CharField(max_length=200)
    amount = models.IntegerField(default =0)
    time_stamp = models.DateTimeField(auto_now_add=True)
    added_to_block = models.BooleanField(default=False)

    def __str__(self):
        return "'%s' transfered '%d' coins to '%s'" % (self.sender, self.amount, self.receiver, )


from faker import Faker
rand = Faker()

class Block(models.Model):
    time_stamp = models.DateTimeField(auto_now_add=False)
    index = models.IntegerField(auto_created=True, blank=True)
    data = models.TextField(blank=True, max_length=255)
    hash = models.CharField(max_length=255, blank=True)
    previous_hash = models.CharField(max_length=255)
    chain = models.ForeignKey(to='Chain', on_delete=models.CASCADE)
    nonce = models.CharField(max_length=255, default=0, blank=True)

    def __str__(self):
        return "Block " + str(self.index) + " on " + self.chain.name

    def __repr__(self):
        return '{}: {}'.format(self.index, str(self.hash)[:6])

    def __hash__(self):
        return sha256(
            u'{}{}{}{}'.format(
                self.index,
                self.data,
                self.previous_hash,
                self.nonce).encode('utf-8')).hexdigest()

    @staticmethod
    def generate_next(latest_block, data):
        block = Block(
            data=data,
            index=latest_block.index + 1,
            time_stamp=datetime.datetime.now(tz=pytz.utc),
            previous_hash=latest_block.hash,
            nonce=SymmetricEncryption.generate_salt(26),
        )
        while not block.valid_hash():
            block.nonce = SymmetricEncryption.generate_salt(26)
        block.hash = block.__hash__()

        # block.save()                # todo: remove

        return block

    def is_valid_block(self, previous_block):
        if self.index != previous_block.index + 1:
            log.warning('%s: Invalid index: %s and %s' % (self.index, self.index, previous_block.index))
            return False
        if self.previous_hash != previous_block.hash:
            log.warning('%s: Invalid previous hash: %s and %s' % (self.index, self.hash, previous_block.hash))
            return False

        if self.__hash__() != self.hash and self.index > 1:
            log.warning('%s: Invalid hash of content: %s and %s' % (self.index, self.hash, self.__hash__()))
            return False
        if not self.valid_hash() and self.index > 1:
            log.warning('%s: Invalid hash value: %s' % (self.index, self.hash))
            return False
        return True

    def valid_hash(self):
        """simulate Proof of work"""
        return self.__hash__()[:4] == '0000'



class Chain(models.Model):
    """
    allows for multiple blockchain entities to exist simultaneously
    """
    time_stamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def __len__(self):
        return self.block_set.count()

    def __repr__(self):
        return '{}: {}'.format(self.name, self.last_block)

    @property
    def last_block(self):
        return self.block_set.order_by('index').last()

    def create_seed(self):
        assert self.pk is not None
        seed = Block.generate_next(
            Block(hash=sha256('seed'.encode('utf-8')).hexdigest(),
                  index=-1),
            data='Seed data',
        )
        seed.chain = self
        seed.save()

    def is_valid_next_block(self, block):
        return block.is_valid_block(self.last_block)

    def add(self, data):
        if not self.block_set.count():
            self.create_seed()

        block = Block.generate_next(
            self.last_block,
            data
        )
        block.chain = self
        return block

    def is_valid_chain(self, blocks=None):
        blocks = blocks or list(self.block_set.order_by('index'))
        if not len(blocks):
            log.warning('Empty chain')
            return False
        if len(blocks) == 1 and blocks[0].index != 0:
            log.warning('Missing seed block in chain.')
            return False
        if not all(pblock.index + 1 == block.index == required_index
                   for pblock, block, required_index in zip(blocks[:-1], blocks[1:], range(1, len(blocks)))):
            log.warning('Chain is not sequential')
            return False
        return all(block.is_valid_block(pblock)
                   for pblock, block in zip(blocks[:-1], blocks[1:]))

    def replace_chain(self, new_chain):
        if self.is_valid_chain(new_chain) and len(new_chain) > len(self):
            self.block_set.all().delete()
            for block in new_chain:
                block.chain = self
                block.save()
                

class Peer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name + "@" + self.address

    def __repr__(self):
        return '{}: {}'.format(self.name, self.address)

    def broadcast(self, chain_name, block):
        from .api.v0.serializers import BlockSerializer
        block_data = BlockSerializer(data=block.__dict__).as_json()
        for peer in Peer.objects.order_by('-id'):
            # import pdb
            # pdb.set_trace()
            print("sending to ", peer)
            JsonApi.post(peer.address,
                         reverse('mine-block', kwargs={'chain_name': chain_name}),
                         data=block_data)

    def query_latest_block(self, chain_name):
        from .api.v0.serializers import BlockSerializer
        data = JsonApi.get(self.address, 
                           reverse('latest-block', kwargs={'chain_name': chain_name}))
        serializer = BlockSerializer(data=data)
        serializer.is_valid()
        instance = Block(**serializer.validated_data)
        instance.chain = Chain.objects.get(name=chain_name)
        return instance

    def query_chain(self, chain_name):
        from .api.v0.serializers import BlockSerializer
        chain = Chain.objects.get(name=chain_name)
        data = JsonApi.get(self.address,
                           reverse('chain',  kwargs={'name': chain_name}))
        blocks = []
        for block_data in data.get('block_set', []):
            serializer = BlockSerializer(data=block_data)
            if serializer.is_valid():
                block = Block(**serializer.validated_data)
                block.chain = chain
                blocks.append(block)
        return blocks

    
    def fetch_longest_chain(self, chain_name):
        chain = max(
            (peer.query_chain(chain_name)
             for peer in self.discover_all_peers()),
            key = len
        )
        return sorted(chain, key = lambda x: x.index)

    
    def mine_block(self, chain_name, data, password=None):
        chain = Chain.objects.get(name=chain_name)
        if password is not None:
            data = EncryptionApi.encrypt(password, data)
        new_block = chain.add(data)
        self.broadcast(chain_name, new_block)


    def synchronize(self, chain_name):
        self.discover_all_peers(commit=True)
        chain = Chain.objects.get(name=chain_name)
        longest_chain = self.fetch_longest_chain(chain_name)
        chain.replace_chain(longest_chain)


    def query_peers(self):
        from .api.v0.serializers import PeerSerializer
        data = JsonApi.get(self.address, reverse('peers'))
        peers = []
        for peer in data:
            serializer = PeerSerializer(data=peer)
            if serializer.is_valid():
                peers.append(Peer(**serializer.validated_data))
        return peers

    @classmethod
    def scan_peers(cls, peers, known_peers):
        known_peers = set(p.address for p in known_peers)
        new_peers = []
        for peer in peers:
            foreign_peers = peer.query_peers()
            for fp in foreign_peers:
                if fp.address not in known_peers:
                    new_peers.append(fp)
        return new_peers

    @classmethod
    def discover_all_peers(cls, commit=False):
        discoveries = Peer.objects.all()
        known_peers = []
        while len(discoveries):
            known_peers.extend(discoveries)
            discoveries = cls.scan_peers(discoveries, known_peers)

        if commit:
            for peer in known_peers:
                peer.save()
        return known_peers



