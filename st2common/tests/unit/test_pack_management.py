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

from st2common.constants.pack_enforcement import PACK_ENFORCEMENT_STATUS_INACTIVE
from st2common.models.db.pack import PackDB
from st2common.persistence.pack import Pack

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACK_ACTIONS_DIR = os.path.join(BASE_DIR, "../../../contrib/packs/actions")
PACK_ACTIONS_DIR = os.path.abspath(PACK_ACTIONS_DIR)

sys.path.insert(0, PACK_ACTIONS_DIR)

from st2common.constants.pack import SYSTEM_PACK_NAMES
from st2common.util.monkey_patch import use_select_poll_workaround

use_select_poll_workaround()

from st2common.util.pack_management import check_license_and_get_pack_enforcement_status, eval_repo_url

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

    def test_pack_in_system_packs_for_check_license_and_get_pack_enforcement_status(self):
        """Test when pack is in SYSTEM_PACK_NAMES."""
        pack_name = "core"
        SYSTEM_PACK_NAMES.append(pack_name)
        result = check_license_and_get_pack_enforcement_status(pack_name)
        self.assertEqual(result, PACK_ENFORCEMENT_STATUS_INACTIVE)
    
    @mock.patch("st2common.util.pack.get_all_packs_with_inactive_pack_enforcement_status_from_db")
    @mock.patch("st2common.content.utils.get_license_info")
    @mock.patch("st2common.util.pack_management._get_pack_enforcement_status")
    @mock.patch.object(Pack, "get_all")
    def test_active_pack_status_with_check_license_and_get_pack_enforcement_status(self, mock_get_all, mock_get_pack_enforcement_status, mock_get_license, mock_get_inactive_packs):
        """Test when pack is NOT in SYSTEM_PACK_NAMES and license check is successful."""
        pack_name = "custom_pack"
        SYSTEM_PACK_NAMES.clear()
        pack1_model_args = {
            "name": "pack1",
            "ref": "pack1",
            "description": "pack1 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "pack_enforcement" : "Inactive",
        }
        pack2_model_args = {
            "name": "pack2",
            "ref": "pack2",
            "description": "pack2 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "pack_enforcement" : "Inactive",
        }
        pack3_model_args = {
            "name": "pack3",
            "ref": "pack3",
            "description": "pack3 pack",
            "version": "0.1.0",
            "author": "Volkswagen",
            "pack_enforcement" : "Inactive",
        }
        mock_get_all.return_value = [
            PackDB(**pack1_model_args),
            PackDB(**pack2_model_args),
            PackDB(**pack3_model_args)
        ]
        mock_get_inactive_packs.return_value = [
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
        mock_get_pack_enforcement_status.return_value = "Active"
        
        result = check_license_and_get_pack_enforcement_status(pack_name)
        self.assertEqual(result, "Active")
