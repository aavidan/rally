# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import random
from collections.abc import Mapping
from typing import Any

import pytest

from esrally.utils import collections


class TestMergeDicts:
    def test_can_merge_empty_dicts(self):
        d1: Mapping[Any, Any] = {}
        d2: Mapping[Any, Any] = {}

        assert dict(collections.merge_dicts(d1, d2)) == {}

    @pytest.mark.parametrize("seed", range(20))
    def test_can_merge_randomized_empty_and_non_empty_dict(self, seed):
        random.seed(seed)

        dct = {"params": {"car-params": {"data_paths": "/mnt/local_ssd"}}}
        d1: Mapping[Any, Any] = random.choice([{}, dct])
        d2: Mapping[Any, Any] = dct if not d1 else {}

        assert dict(collections.merge_dicts(d1, d2)) == dct

    def test_can_merge_nested_dicts(self):
        d1 = {
            "params": {
                "car": "4gheap",
                "car-params": {"additional_cluster_settings": {"indices.queries.cache.size": "5%", "transport.tcp.compress": True}},
                "unique-param": "foobar",
            }
        }

        d2 = {"params": {"car-params": {"data_paths": "/mnt/local_ssd"}}}

        assert dict(collections.merge_dicts(d1, d2)) == {
            "params": {
                "car-params": {
                    "additional_cluster_settings": {"indices.queries.cache.size": "5%", "transport.tcp.compress": True},
                    "data_paths": "/mnt/local_ssd",
                },
                "car": "4gheap",
                "unique-param": "foobar",
            }
        }

    def test_can_merge_nested_lists_in_dicts(self):
        d1 = {"params": {"foo": [1, 2, 3]}}

        d2 = {"params": {"foo": [3, 4, 5]}}

        assert dict(collections.merge_dicts(d1, d2)) == {"params": {"foo": [1, 2, 3, 4, 5]}}

    def test_can_merge_nested_booleans_in_dicts(self):
        d1 = {"params": {"foo": True, "other": [1, 2, 3]}}

        d2 = {"params": {"foo": False}}

        assert dict(collections.merge_dicts(d1, d2)) == {
            "params": {
                # d2 wins
                "foo": False,
                "other": [1, 2, 3],
            }
        }


class TestDeepUpdate:
    def testcan_update_empty_dict(self):
        d1 = {}
        d2 = {}

        collections.deep_update(d1, d2)

        assert d1 == d2
        assert d1 is not d2

    def test_can_update_with_no_update(self):
        d1 = {"foo": "bar"}

        collections.deep_update(d1)

        assert d1 is not None
        assert d1["foo"] == "bar"

    def test_can_update_with_empty_dict(self):
        d1 = {"foo": "bar"}
        d2 = {}

        collections.deep_update(d1, d2)

        assert d1 is not None
        assert d1 is not d2
        assert d1["foo"] == "bar"

    def test_can_update_empty_dict(self):
        d1 = {}
        d2 = {"foo": "bar"}

        collections.deep_update(d1, d2)

        assert d1 == d2
        assert d1 is not d2
        assert d1["foo"] == "bar"

    def test_can_update_non_empty_dict(self):
        d1 = {"foo": "bar"}
        d2 = {"foo": "baz"}

        collections.deep_update(d1, d2)

        assert d1 == d2
        assert d1 is not d2
        assert d1["foo"] == "baz"

    def test_can_update_nested_dict(self):
        d1 = {"foo": {"bar": "baz"}}
        d2 = {"foo": {"bar": "qux"}}

        collections.deep_update(d1, d2)

        assert d1 == d2
        assert d1 is not d2
        assert d1["foo"]["bar"] == "qux"

    def test_can_update_nested_list(self):
        d1 = {"foo": [1, 2, 3]}
        d2 = {"foo": [3, 4, 5]}

        collections.deep_update(d1, d2)

        assert d1 == d2
        assert d1 is not d2
        assert d1["foo"] == [3, 4, 5]

    @pytest.mark.parametrize("seed", range(20))
    def test_can_update_randomized_empty_and_non_empty_dict(self, seed):
        random.seed(seed)

        dct = {"params": {"car-params": {"data_paths": "/mnt/local_ssd"}}}
        d1: Mapping[Any, Any] = random.choice([{}, dct])
        d2: Mapping[Any, Any] = dct if not d1 else {}

        collections.deep_update(d1, d2)

        assert d1 == dct

    def test_can_update_nested_dicts(self):
        d1 = {
            "params": {
                "car": "4gheap",
                "car-params": {"additional_cluster_settings": {"indices.queries.cache.size": "5%", "transport.tcp.compress": True}},
                "unique-param": "foobar",
            }
        }

        d2 = {"params": {"car-params": {"data_paths": "/mnt/local_ssd"}}}
        collections.deep_update(d1, d2)

        assert d1 == {
            "params": {
                "car-params": {
                    "additional_cluster_settings": {"indices.queries.cache.size": "5%", "transport.tcp.compress": True},
                    "data_paths": "/mnt/local_ssd",
                },
                "car": "4gheap",
                "unique-param": "foobar",
            }
        }

    def test_nested_updates_are_deep_copied(self):
        d1 = {"foo": {"bar": "baz"}}
        d2 = {"foo": {"bar": [1, 2, 3]}}
        collections.deep_update(d1, d2)

        assert d1 is not d2  # type: ignore[comparison-overlap]
        assert d1["foo"] is not d2["foo"]  # type: ignore[comparison-overlap]
        assert d1["foo"]["bar"] is not d2["foo"]["bar"]  # type: ignore[comparison-overlap]
        assert d1["foo"]["bar"] == [1, 2, 3]  # type: ignore[comparison-overlap]
