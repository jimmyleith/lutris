from unittest import TestCase
from lutris.installer import ScriptInterpreter, ScriptingError


class MockInterpreter(ScriptInterpreter):
    """ a script interpreter mock """
    script = {'runner': 'linux'}

    def is_valid(self):
        return True


class TestScriptInterpreter(TestCase):
    def test_script_with_correct_values_is_valid(self):
        script = {
            'runner': 'wine',
            'installer': 'bar',
            'name': 'baz',
            'game_slug': 'baz',
        }
        interpreter = ScriptInterpreter(script, None)
        self.assertFalse(interpreter.errors)
        self.assertTrue(interpreter.is_valid())

    def test_move_requires_src_and_dst(self):
        script = {
            'foo': 'bar',
            'installer': {},
            'name': 'missing_runner',
            'game_slug': 'missing-runner'
        }
        with self.assertRaises(ScriptingError):
            interpreter = ScriptInterpreter(script, None)
            interpreter._get_move_paths({})

    def test_get_command_returns_a_method(self):
        interpreter = MockInterpreter({}, None)
        command, params = interpreter._map_command({'move': 'whatever'})
        self.assertIn("bound method MockInterpreter.move", str(command))
        self.assertEqual(params, "whatever")

    def test_get_command_doesnt_return_private_methods(self):
        """ """
        interpreter = MockInterpreter({}, None)
        with self.assertRaises(ScriptingError) as ex:
            command, params = interpreter._map_command(
                {'_substitute': 'foo'}
            )
        self.assertEqual(ex.exception.message,
                         "The command substitute does not exists")
