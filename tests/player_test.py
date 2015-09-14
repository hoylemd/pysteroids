from pyglet.window import key
from game.player import Player
from game import resources
from tests.scaffolding import fps_to_s, eq_within_epsilon


def test_init__initial_values():
    sut = Player(img=resources.player_image)

    assert sut.thrust == 200.0
    assert sut.maneuvering_thrust == 360.0

    assert sut.x == 0.0
    assert sut.y == 0.0

    assert sut.center_x == 0.0
    assert sut.center_y == 0.0

    for sut_key in sut.keys:
        assert not sut.keys[sut_key]

    for signal in sut.signals:
        assert not sut.signals[signal]


def test_init__specified_values():
    sut = Player(img=resources.player_image, x=123.4, y=421.54, thrust=150.0,
                 maneuvering_thrust=500.0)

    assert sut.thrust == 150.0
    assert sut.maneuvering_thrust == 500.0

    assert sut.x == 123.4
    assert sut.y == 421.54

    assert sut.center_x == 123.4
    assert sut.center_y == 421.54


def test_key_press__left():
    sut = Player(img=resources.player_image, x=200, y=300)

    sut.on_key_press(key.LEFT, None)

    assert sut.keys['left']

    sut.on_key_release(key.LEFT, None)

    assert not sut.keys['left']


def test_key_press__right():
    sut = Player(img=resources.player_image, x=200, y=300)

    sut.on_key_press(key.RIGHT, None)

    assert sut.keys['right']

    sut.on_key_release(key.RIGHT, None)

    assert not sut.keys['right']


def test_key_press__up():
    sut = Player(img=resources.player_image, x=200, y=300)

    sut.on_key_press(key.UP, None)

    assert sut.keys['up']

    sut.on_key_release(key.UP, None)

    assert not sut.keys['up']


def test_key_press__down():
    sut = Player(img=resources.player_image, x=200, y=300)

    sut.on_key_press(key.DOWN, None)

    assert sut.keys['down']

    sut.on_key_release(key.DOWN, None)

    assert not sut.keys['down']


def test_key_press__space():
    sut = Player(img=resources.player_image, x=200, y=300)

    sut.on_key_press(key.SPACE, None)

    assert sut.signals['recenter']


def set_up_sluggish_player():
    return Player(img=resources.player_image, x=200.0, y=300.0, thrust=10.0,
                  maneuvering_thrust=15.0)


def test_init__sluggish():
    sut = set_up_sluggish_player()

    assert sut.rotation_speed == 0.0
    assert sut.rotation == 0.0
    assert sut.velocity_x == 0.0
    assert sut.velocity_y == 0.0
    assert sut.x == 200.0
    assert sut.y == 300.0


def test_update__turn_right():
    sut = set_up_sluggish_player()

    # turn right
    sut.on_key_press(key.RIGHT, None)

    sut.update(fps_to_s(60)) # one 60 fps frame

    assert sut.rotation_speed == 0.25
    assert eq_within_epsilon(sut.rotation, 0.0021, 0.0001)

    sut.update(fps_to_s(60) * 59)  # finish this second

    sut.on_key_release(key.RIGHT, None)

    assert sut.rotation_speed == 15.0
    assert eq_within_epsilon(sut.rotation, 7.5)

    sut.update(1.0)  # one second

    assert sut.rotation_speed == 15.0
    assert eq_within_epsilon(sut.rotation, 29.75)


def test_update__turn_left():
    sut = set_up_sluggish_player()

    # turn left
    sut.on_key_press(key.LEFT, None)

    sut.update(fps_to_s(90))

    assert sut.rotation_speed == -0.375
    assert eq_within_epsilon(sut.rotation, -0.0021, 0.0001)

    sut.update(fps_to_s(60) * 59)  # finish this second

    sut.on_key_release(key.RIGHT, None)

    assert sut.rotation_speed == 15.0
    assert eq_within_epsilon(sut.rotation, 14.75)

    sut.update(1.0)  # one second

    assert sut.rotation_speed == 15.0
    assert eq_within_epsilon(sut.rotation, 29.75)


def skip_update__SAS():
    sut = set_up_sluggish_player()

    # engage SAS
    sut.on_key_press(key.DOWN, None)

    sut.update(1.0)  # stabilize for one second

    assert sut.rotation_speed == 0.0
    assert eq_within_epsilon(sut.rotation, 45.00)

    sut.on_key_release(key.DOWN, None)

    sut.update(fps_to_s(60))

    assert sut.rotation_speed == 0.0
    assert sut.rotation == 30.0
    assert sut.velocity_x == 0.0
    assert sut.velocity_y == 0.0
    assert sut.x == 200.0
    assert sut.y == 300.0

    # thrust
    sut.on_key_press(key.UP, None)

    sut.update(fps_to_s(60))

    assert sut.rotation_speed == 0.0
    assert sut.rotation == 30.0
    assert eq_within_epsilon(sut.velocity_x, 4.99, 0.1)
    assert eq_within_epsilon(sut.velocity_y, 8.66, 0.1)
    assert eq_within_epsilon(sut.x, 200.08, 0.1)
    assert eq_within_epsilon(sut.y, 300.10, 0.1)

    sut.update(fps_to_s(60))

    assert eq_within_epsilon(sut.velocity_x, 9.99, 0.1)
    assert eq_within_epsilon(sut.velocity_y, 17.33, 0.1)
    assert eq_within_epsilon(sut.x, 200.24, 0.1)
    assert eq_within_epsilon(sut.y, 300.43, 0.1)

    # coast
    sut.on_key_release(key.UP, None)

    sut.update(fps_to_s(60))

    assert eq_within_epsilon(sut.velocity_x, 9.99, 0.1)
    assert eq_within_epsilon(sut.velocity_y, 17.33, 0.1)
    assert eq_within_epsilon(sut.x, 200.40, 0.1)
    assert eq_within_epsilon(sut.y, 300.76, 0.1)

    sut.update(5.0)  # wait for 5 seconds)

    assert eq_within_epsilon(sut.velocity_x, 9.99, 0.1)
    assert eq_within_epsilon(sut.velocity_y, 17.33, 0.1)
    assert eq_within_epsilon(sut.x, 250.42, 0.1)
    assert eq_within_epsilon(sut.y, 387.32, 0.1)

    # artificially turn southish

    sut.velocity_x = 0.0
    sut.velocity_y = 0.0
    sut.rotation = 195.0

    # thrust again
    sut.on_key_press(key.UP, None)

    sut.update(0.25)  # go for a quarter second
    assert eq_within_epsilon(sut.velocity_x, -1, 0.1)
    assert eq_within_epsilon(sut.velocity_y, 17.33, 0.1)
    assert eq_within_epsilon(sut.x, 250.42, 0.1)
    assert eq_within_epsilon(sut.y, 387.32, 0.1)
