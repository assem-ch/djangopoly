# Test views in the Monopoly application

from django.test import TestCase, Client
from monopoly.models import *

class TestIndex(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

class TestGameCreation(TestCase):
    def setUp(self):
        self.client = Client()

    def test_game_creation_public(self):
        response = self.client.get('/new_game/public', follow=True)
        self.assertFalse(Game.objects.all()[0].private)

    def test_game_creation_private(self):
        response = self.client.get('/new_game/private', follow=True)
        self.assertTrue(Game.objects.all()[0].private)

    def test_game_creation(self):
        response = self.client.get('/new_game/public', follow=True)
        self.assertEquals(Game.objects.all().count(), 1) # One game created
        game = Game.objects.all()[0]
        self.assertEquals(game.square_set.count(), 40) # There should be 40 squares in the game

class TestGameJoin(TestCase):
    def setUp(self):
        Client().get('/new_game/public', follow=True)
        Client().get('/new_game/public', follow=True)
        self.game1 = Game.objects.all()[0]
        self.game2 = Game.objects.all()[1]
        self.clients = []
        for i in range(4):
            self.clients.append(Client())
    
    def test_join_game(self):
        client = self.clients[0]
        self.client.get('/game/{0}/'.format(self.game1.id))
        player = Player.objects.get(session_id=self.client.session.session_key)
        self.assertEquals(player.game, self.game1)

    def test_turn_initialisation(self):
        for client in self.clients:
            client.get('/game/{0}/'.format(self.game1.id))
        
        expected_plays_in_turns = 0
        for client in self.clients:
            player = Player.objects.get(session_id=client.session.session_key)
            self.assertEquals(player.plays_in_turns, expected_plays_in_turns)
            expected_plays_in_turns += 1
        
    def test_join_different_game(self):
        client = self.clients[0]
        client.get('/game/{0}/'.format(self.game1.id))
        response = client.get('/game/{0}/'.format(self.game1.id))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)

