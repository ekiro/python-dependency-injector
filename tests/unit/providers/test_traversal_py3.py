import unittest

from dependency_injector import providers


class TraverseTests(unittest.TestCase):

    def test_traverse_cycled_graph(self):
        provider1 = providers.Provider()

        provider2 = providers.Provider()
        provider2.override(provider1)

        provider3 = providers.Provider()
        provider3.override(provider2)

        provider1.override(provider3)  # Cycle: provider3 -> provider2 -> provider1 -> provider3

        all_providers = list(providers.traverse(provider1))

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)

    def test_traverse_types_filtering(self):
        provider1 = providers.Resource(dict)
        provider2 = providers.Resource(dict)
        provider3 = providers.Provider()

        provider = providers.Provider()

        provider.override(provider1)
        provider.override(provider2)
        provider.override(provider3)

        all_providers = list(providers.traverse(provider, types=[providers.Resource]))

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)


class ProviderTests(unittest.TestCase):

    def test_traversal_overriding(self):
        provider1 = providers.Provider()
        provider2 = providers.Provider()
        provider3 = providers.Provider()

        provider = providers.Provider()

        provider.override(provider1)
        provider.override(provider2)
        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)

    def test_traversal_overriding_nested(self):
        provider1 = providers.Provider()

        provider2 = providers.Provider()
        provider2.override(provider1)

        provider3 = providers.Provider()
        provider3.override(provider2)

        provider = providers.Provider()
        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)

    def test_traverse_types_filtering(self):
        provider1 = providers.Resource(dict)
        provider2 = providers.Resource(dict)
        provider3 = providers.Provider()

        provider = providers.Provider()

        provider.override(provider1)
        provider.override(provider2)
        provider.override(provider3)

        all_providers = list(provider.traverse(types=[providers.Resource]))

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)


class ObjectTests(unittest.TestCase):

    def test_traversal(self):
        provider = providers.Object('string')
        all_providers = list(provider.traverse())
        self.assertEqual(len(all_providers), 0)

    def test_traversal_provider(self):
        another_provider = providers.Provider()
        provider = providers.Object(another_provider)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 1)
        self.assertIn(another_provider, all_providers)

    def test_traversal_provider_and_overriding(self):
        another_provider_1 = providers.Provider()
        another_provider_2 = providers.Provider()
        another_provider_3 = providers.Provider()

        provider = providers.Object(another_provider_1)

        provider.override(another_provider_2)
        provider.override(another_provider_3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(another_provider_1, all_providers)
        self.assertIn(another_provider_2, all_providers)
        self.assertIn(another_provider_3, all_providers)


class DelegateTests(unittest.TestCase):

    def test_traversal_provider(self):
        another_provider = providers.Provider()
        provider = providers.Delegate(another_provider)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 1)
        self.assertIn(another_provider, all_providers)

    def test_traversal_provider_and_overriding(self):
        provider1 = providers.Provider()
        provider2 = providers.Provider()

        provider3 = providers.Provider()
        provider3.override(provider2)

        provider = providers.Delegate(provider1)

        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)


class DependencyTests(unittest.TestCase):

    def test_traversal(self):
        provider = providers.Dependency()
        all_providers = list(provider.traverse())
        self.assertEqual(len(all_providers), 0)

    def test_traversal_default(self):
        another_provider = providers.Provider()
        provider = providers.Dependency(default=another_provider)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 1)
        self.assertIn(another_provider, all_providers)

    def test_traversal_overriding(self):
        provider1 = providers.Provider()

        provider2 = providers.Provider()
        provider2.override(provider1)

        provider = providers.Dependency()
        provider.override(provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)


class DependenciesContainerTests(unittest.TestCase):

    def test_traversal(self):
        provider = providers.DependenciesContainer()
        all_providers = list(provider.traverse())
        self.assertEqual(len(all_providers), 0)

    def test_traversal_default(self):
        another_provider = providers.Provider()
        provider = providers.DependenciesContainer(default=another_provider)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 1)
        self.assertIn(another_provider, all_providers)

    def test_traversal_fluent_interface(self):
        provider = providers.DependenciesContainer()
        provider1 = provider.provider1
        provider2 = provider.provider2

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traversal_overriding(self):
        provider1 = providers.Provider()
        provider2 = providers.Provider()
        provider3 = providers.DependenciesContainer(
            provider1=provider1,
            provider2=provider2,
        )

        provider = providers.DependenciesContainer()
        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 5)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)
        self.assertIn(provider.provider1, all_providers)
        self.assertIn(provider.provider2, all_providers)


class CallableTests(unittest.TestCase):

    def test_traverse(self):
        provider = providers.Callable(dict)
        all_providers = list(provider.traverse())
        self.assertEqual(len(all_providers), 0)

    def test_traverse_args(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')
        provider = providers.Callable(list, 'foo', provider1, provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_kwargs(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')
        provider = providers.Callable(dict, foo='foo', bar=provider1, baz=provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_overridden(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')

        provider = providers.Callable(dict, 'foo')
        provider.override(provider1)
        provider.override(provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_provides(self):
        provider1 = providers.Callable(list)
        provider2 = providers.Object('bar')
        provider3 = providers.Object('baz')

        provider = providers.Callable(provider1, provider2)
        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)


class ConfigurationTests(unittest.TestCase):

    def test_traverse(self):
        config = providers.Configuration(default={'option1': {'option2': 'option2'}})
        option1 = config.option1
        option2 = config.option1.option2
        option3 = config.option1[config.option1.option2]

        all_providers = list(config.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(option1, all_providers)
        self.assertIn(option2, all_providers)
        self.assertIn(option3, all_providers)

    def test_traverse_typed(self):
        config = providers.Configuration()
        option = config.option
        typed_option = config.option.as_int()

        all_providers = list(typed_option.traverse())

        self.assertEqual(len(all_providers), 1)
        self.assertIn(option, all_providers)

    def test_traverse_overridden(self):
        options = {'option1': {'option2': 'option2'}}
        config = providers.Configuration()
        config.from_dict(options)

        all_providers = list(config.traverse())

        self.assertEqual(len(all_providers), 1)
        overridden, = all_providers
        self.assertEqual(overridden(), options)
        self.assertIs(overridden, config.last_overriding)

    def test_traverse_overridden_option_1(self):
        options = {'option2': 'option2'}
        config = providers.Configuration()
        config.option1.from_dict(options)

        all_providers = list(config.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(config.option1, all_providers)
        self.assertIn(config.last_overriding, all_providers)

    def test_traverse_overridden_option_2(self):
        options = {'option2': 'option2'}
        config = providers.Configuration()
        config.option1.from_dict(options)

        all_providers = list(config.option1.traverse())

        self.assertEqual(len(all_providers), 0)


class FactoryTests(unittest.TestCase):

    def test_traverse(self):
        provider = providers.Factory(dict)
        all_providers = list(provider.traverse())
        self.assertEqual(len(all_providers), 0)

    def test_traverse_args(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')
        provider = providers.Factory(list, 'foo', provider1, provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_kwargs(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')
        provider = providers.Factory(dict, foo='foo', bar=provider1, baz=provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_attributes(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')
        provider = providers.Factory(dict)
        provider.add_attributes(foo='foo', bar=provider1, baz=provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_overridden(self):
        provider1 = providers.Object('bar')
        provider2 = providers.Object('baz')

        provider = providers.Factory(dict, 'foo')
        provider.override(provider1)
        provider.override(provider2)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 2)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)

    def test_traverse_provides(self):
        provider1 = providers.Callable(list)
        provider2 = providers.Object('bar')
        provider3 = providers.Object('baz')

        provider = providers.Factory(provider1, provider2)
        provider.override(provider3)

        all_providers = list(provider.traverse())

        self.assertEqual(len(all_providers), 3)
        self.assertIn(provider1, all_providers)
        self.assertIn(provider2, all_providers)
        self.assertIn(provider3, all_providers)
