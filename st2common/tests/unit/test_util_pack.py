# Copyright 2020 The StackStorm Authors.
# Copyright 2019 Extreme Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
import mock
import unittest2

from st2common.models.db.pack import PackDB
from st2common.persistence.pack import Pack
from st2common.util.pack import get_all_enabled_packs_from_db, get_pack_common_libs_path_for_pack_db
from st2common.util.pack import get_pack_warnings
from st2common.util.pack import get_pack_ref_from_metadata
from st2common.util.pack import get_pack_common_libs_path_for_pack_db


class PackUtilsTestCase(unittest2.TestCase):
    def test_get_pack_common_libs_path_for_pack_db(self):
        pack_model_args = {
            "name": "Yolo CI",
            "ref": "yolo_ci",
            "description": "YOLO CI pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "path": "/opt/stackstorm/packs/yolo_ci/",
        }
        pack_db = PackDB(**pack_model_args)
        lib_path = get_pack_common_libs_path_for_pack_db(pack_db)
        self.assertEqual("/opt/stackstorm/packs/yolo_ci/lib", lib_path)

    def test_get_pack_common_libs_path_for_pack_db_no_path_in_pack_db(self):
        pack_model_args = {
            "name": "Yolo CI",
            "ref": "yolo_ci",
            "description": "YOLO CI pack",
            "version": "0.1.0",
            "author": "Volkswagen",
        }
        pack_db = PackDB(**pack_model_args)
        lib_path = get_pack_common_libs_path_for_pack_db(pack_db)
        self.assertEqual(None, lib_path)

    def test_get_pack_warnings_python2_only(self):
        pack_metadata = {"python_versions": ["2"], "name": "Pack2"}
        warning = get_pack_warnings(pack_metadata)
        self.assertTrue("DEPRECATION WARNING" in warning)

    def test_get_pack_warnings_python3_only(self):
        pack_metadata = {"python_versions": ["3"], "name": "Pack3"}
        warning = get_pack_warnings(pack_metadata)
        self.assertEqual(None, warning)

    def test_get_pack_warnings_python2_and_3(self):
        pack_metadata = {"python_versions": ["2", "3"], "name": "Pack23"}
        warning = get_pack_warnings(pack_metadata)
        self.assertEqual(None, warning)

    def test_get_pack_warnings_no_python(self):
        pack_metadata = {"name": "PackNone"}
        warning = get_pack_warnings(pack_metadata)
        self.assertEqual(None, warning)

    def test_get_pack_ref_from_meta_name_valid(self):
        pack_metadata = {"name": "pack1"}
        pack_ref = get_pack_ref_from_metadata(pack_metadata)
        self.assertEqual("pack1", pack_ref)

    def test_get_pack_ref_from_meta_ref_valid(self):
        pack_metadata = {"name": "Pack1", "ref": "pack1"}
        pack_ref = get_pack_ref_from_metadata(pack_metadata)
        self.assertEqual("pack1", pack_ref)

    def test_get_pack_ref_from_meta_ref_global(self):
        pack_metadata = {"name": "Pack1", "ref": "_global"}
        self.assertRaises(ValueError, get_pack_ref_from_metadata, pack_metadata)

    def test_get_pack_ref_from_meta_name_global(self):
        pack_metadata = {"name": "_global"}
        self.assertRaises(ValueError, get_pack_ref_from_metadata, pack_metadata)
    
    @mock.patch.object(Pack, "get_all")
    def test_packs_with_pack_enabled_True_status_from_db(self, mock_get_all):
        """Test when packs status is True from pack db."""
        pack1_model_args = {
            "name": "pack1",
            "ref": "pack1",
            "description": "pack1 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "enabled" : True,
        }
        pack2_model_args = {
            "name": "pack2",
            "ref": "pack2",
            "description": "pack2 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "enabled" : False,
        }
        pack3_model_args = {
            "name": "pack3",
            "ref": "pack3",
            "description": "pack3 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "enabled" : True,
        }
        mock_get_all.return_value = [
            PackDB(**pack1_model_args),
            PackDB(**pack2_model_args),
            PackDB(**pack3_model_args)
        ]
        result = get_all_enabled_packs_from_db()
        self.assertEqual(result, ["pack1", "pack3"])
    
    @mock.patch.object(Pack, "get_all")
    def test_no_packs_found_with_pack_enabled_True_status_from_db(self, mock_get_all):
        """Test when there are no packs in the database."""
        mock_get_all.return_value = []
        result = get_all_enabled_packs_from_db()
        self.assertEqual(result, [])
    
    @mock.patch.object(Pack, "get_all")
    def test_packs_for_pack_enabled_False_status_from_db(self, mock_get_all):
        """Test when packs status is False from pack db."""
        pack1_model_args = {
            "name": "pack1",
            "ref": "pack1",
            "description": "pack1 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "enabled" : False,
        }
        pack2_model_args = {
            "name": "pack2",
            "ref": "pack2",
            "description": "pack2 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "enabled" : False,
        }
        mock_get_all.return_value = [
            PackDB(**pack1_model_args),
            PackDB(**pack2_model_args)
        ]
        result = get_all_enabled_packs_from_db()
        self.assertEqual(result, [])
