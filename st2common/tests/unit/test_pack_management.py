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

import os
import sys

import mock
import unittest2

from st2common.models.db.pack import PackDB
from st2common.persistence.pack import Pack

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACK_ACTIONS_DIR = os.path.join(BASE_DIR, "../../../contrib/packs/actions")
PACK_ACTIONS_DIR = os.path.abspath(PACK_ACTIONS_DIR)

sys.path.insert(0, PACK_ACTIONS_DIR)

from st2common.constants.pack import DEFAULT_PACK_NAME, SYSTEM_PACK_NAMES
from st2common.util.monkey_patch import use_select_poll_workaround

use_select_poll_workaround()

from st2common.util.pack_management import _get_pack_status, check_license_and_get_pack_status, eval_repo_url

__all__ = ["InstallPackTestCase"]


class InstallPackTestCase(unittest2.TestCase):
    def test_eval_repo(self):
        result = eval_repo_url("stackstorm/st2contrib")
        self.assertEqual(result, "https://github.com/stackstorm/st2contrib")

        result = eval_repo_url("git@github.com:StackStorm/st2contrib.git")
        self.assertEqual(result, "git@github.com:StackStorm/st2contrib.git")

        result = eval_repo_url("gitlab@gitlab.com:StackStorm/st2contrib.git")
        self.assertEqual(result, "gitlab@gitlab.com:StackStorm/st2contrib.git")

        repo_url = "https://github.com/StackStorm/st2contrib.git"
        result = eval_repo_url(repo_url)
        self.assertEqual(result, repo_url)

        repo_url = "https://git-wip-us.apache.org/repos/asf/libcloud.git"
        result = eval_repo_url(repo_url)
        self.assertEqual(result, repo_url)

    def test_pack_in_system_packs_for_check_license_and_get_pack_enabled_status_True(self):
        """Test when pack is in SYSTEM_PACK_NAMES."""
        pack_name = "core"
        SYSTEM_PACK_NAMES.append(pack_name)
        result = check_license_and_get_pack_status(pack_name)
        self.assertEqual(result, True)
    
    def test_pack_in_default_pack_name_for_check_license_and_get_pack_enabled_status_True(self):
        """Test when pack is DEFAULT_PACK_NAME."""
        pack_name = DEFAULT_PACK_NAME
        SYSTEM_PACK_NAMES.append(pack_name)
        result = check_license_and_get_pack_status(pack_name)
        self.assertEqual(result, True)
    
    @mock.patch("st2common.util.pack.get_all_enabled_packs_from_db")
    @mock.patch("st2common.content.utils.get_license_info")
    @mock.patch("st2common.util.pack_management._get_pack_status")
    @mock.patch.object(Pack, "get_all")
    def test_check_license_and_get_pack_status_False(self, mock_get_all, mock_get_pack_status, mock_get_license, mock_get_enabled_packs):
        """Test when pack is NOT in SYSTEM_PACK_NAMES or pack is not DEFAULT_PACK_NAME and checks license for pack returning False."""
        pack_name = "custom_pack"
        SYSTEM_PACK_NAMES.clear()
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
            "enabled" : True,
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
        mock_get_enabled_packs.return_value = [
            PackDB(**pack1_model_args),
            PackDB(**pack2_model_args),
            PackDB(**pack3_model_args)
        ]
        mock_get_license.return_value = {
            "license": {
                "token": "JZDYOLisioB4i5IC",
                "expires": "2025-04-14T00:00:00Z",
                "grace": 30,
                "capabilities": ["netapp", "packs", "basic"],
                "description": {
                    "netapp": {"device_count": 4},
                    "packs": {"count": 3}
                }
            },
            "valid": "True"
        }
        mock_get_pack_status.return_value = False
        
        result = check_license_and_get_pack_status(pack_name)
        self.assertEqual(result, False)
    
    @mock.patch("st2common.util.pack.get_all_enabled_packs_from_db")
    @mock.patch("st2common.content.utils.get_license_info")
    @mock.patch("st2common.util.pack_management._get_pack_status")
    @mock.patch.object(Pack, "get_all")
    def test_check_license_and_get_pack_status_True(self, mock_get_all, mock_get_pack_status, mock_get_license, mock_get_enabled_packs):
        """Test when pack is NOT in SYSTEM_PACK_NAMES or pack is not DEFAULT_PACK_NAME and checks license for pack returning True"""
        pack_name = "custom_pack"
        SYSTEM_PACK_NAMES.clear()
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
            "enabled" : True,
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
        mock_get_enabled_packs.return_value = [
            PackDB(**pack1_model_args),
            PackDB(**pack2_model_args),
            PackDB(**pack3_model_args)
        ]
        mock_get_license.return_value = {
            "license": {
                "token": "JZDYOLisioB4i5IC",
                "expires": "2025-04-14T00:00:00Z",
                "grace": 30,
                "capabilities": ["netapp", "packs", "basic"],
                "description": {
                    "netapp": {"device_count": 4},
                    "packs": {"count": 4}
                }
            },
            "valid": "True"
        }
        mock_get_pack_status.return_value = True
        
        result = check_license_and_get_pack_status(pack_name)
        self.assertEqual(result, True)

    def test_license_with_pack_capability_and_adding_new_pack_returns_pack_status_False(self):
        """Test when license has pack capability and license count is 2 and we add new pack returing pack enabled status as False"""
        license_info = {
            "license": {
                "capabilities": ["packs"],
                "description": {"packs": {"count": 2}}
            }
        }
        enabled_packs = ["pack1", "pack2"]
        result = _get_pack_status(license_info, enabled_packs, "pack3")
        self.assertEqual(result, False)

    def test_license_with_pack_capability_and_adding_new_pack_returns_pack_status_True(self):
        """Test when license has pack capability and license count is 3 and we add new pack returing pack enabled status as True"""
        license_info = {
            "license": {
                "capabilities": ["packs"],
                "description": {"packs": {"count": 3}}
            }
        }
        enabled_packs = ["pack1","pack2"]
        result = _get_pack_status(license_info, enabled_packs, "pack3")
        self.assertEqual(result, True)

    def test_license_without_packs_capability_raises_value_error(self):
        """Test when license does not have the pack capabilities returing error"""
        license_info = {
            "license": {
                "capabilities": ["basic"]
            }
        }
        with self.assertRaises(ValueError) as context:
            _get_pack_status(license_info, [], "pack1")
        self.assertIn("License not found or capabilities to install packs", str(context.exception))
