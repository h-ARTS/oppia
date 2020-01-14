# Copyright 2020 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for scripts/check_e2e_tests_are_captured_in_ci.py."""
from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import os

from core.tests import test_utils
import python_utils
import utils

from . import check_e2e_tests_are_captured_in_ci

DUMMY_TEST_SUITES = ['oneword', 'twoWords']

DUMMY_CONF_FILES = os.path.join(
    os.getcwd(), 'core', 'tests', 'data', 'dummy_ci_tests')


class CheckE2eTestsCapturedInCI(test_utils.GenericTestBase):
    """Test the methods which performs travis.yml and
    protractor.conf.js sync checks.
    """

    def _mock_tests_to_remove(self):
        return self.swap(check_e2e_tests_are_captured_in_ci,
            'TEST_SUITES_NOT_RUN_ON_TRAVIS', [])

    def _mock_read_protractor_conf_file(self):
        protractor_config_file = python_utils.open_file(
            os.path.join(
                DUMMY_CONF_FILES, 'dummy_protractor.conf.js'), 'r').read()
        return protractor_config_file

    def _mock_read_travis_yml_file(self):
        travis_ci_file = python_utils.open_file(
            os.path.join(
                DUMMY_CONF_FILES, '.dummy_travis.yml'), 'r').read()
        travis_ci_dict = utils.dict_from_yaml(travis_ci_file)
        return travis_ci_dict

    def _mock_read_protractor_conf_file_fail(self):
        protractor_config_file = python_utils.open_file(
            os.path.join(
                DUMMY_CONF_FILES, 'protractor_has_extra_test.conf.js'),
                'r').read()
        return protractor_config_file

    def _mock_read_travis_yml_file_fail(self):
        travis_ci_file = python_utils.open_file(
            os.path.join(
                DUMMY_CONF_FILES, '.travis_has_extra_test.yml'), 'r').read()
        travis_ci_dict = utils.dict_from_yaml(travis_ci_file)
        return travis_ci_dict

    def _return_empty_list(self):
        return []

    def test_read_travis_ci_file(self):
        travis_ci_file = os.path.join(
                DUMMY_CONF_FILES, '.dummy_travis.yml')

        travis_ci_file_swap = self.swap(
            check_e2e_tests_are_captured_in_ci, 'TRAVIS_CI_FILE_PATH',
            travis_ci_file)
        with travis_ci_file_swap:
            actual_travis_ci_dict = (
                check_e2e_tests_are_captured_in_ci
                .read_and_parse_travis_yml_file())
            self.assertEqual(TRAVIS_CI_DICT, actual_travis_ci_dict)

    def test_read_protractor_file(self):
        protractor_config_file = os.path.join(
                DUMMY_CONF_FILES, 'dummy_protractor.conf.js')

        protractor_config_file_swap = self.swap(
            check_e2e_tests_are_captured_in_ci, 'PROTRACTOR_CONF_FILE_PATH',
            protractor_config_file)
        with protractor_config_file_swap:
            actual_protractor_config_file = (
                check_e2e_tests_are_captured_in_ci.read_protractor_conf_file())
        self.assertEqual(DUMMY_PROTRACTOR_CONF_FILE,
                         actual_protractor_config_file)

    def test_get_e2e_suite_names_from_jobs_travis_yml_file(self):
        dummy_path = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'read_and_parse_travis_yml_file', self._mock_read_travis_yml_file)
        with dummy_path:
            actual_travis_jobs = (
                check_e2e_tests_are_captured_in_ci
                .get_e2e_suite_names_from_jobs_travis_yml_file())
        self.assertEqual(DUMMY_TEST_SUITES, actual_travis_jobs)

    def test_get_e2e_suite_names_from_script_travis_yml_file(self):
        dummy_path = self.swap(check_e2e_tests_are_captured_in_ci,
           'read_and_parse_travis_yml_file',self._mock_read_travis_yml_file)
        with dummy_path:
            actual_travis_script = (
                check_e2e_tests_are_captured_in_ci
                .get_e2e_suite_names_from_script_travis_yml_file())
        self.assertEqual(DUMMY_TEST_SUITES, actual_travis_script)

    def test_get_e2e_suite_names_from_script_travis_yml_file_fail(self):
        dummy_path = self.swap(check_e2e_tests_are_captured_in_ci,
                   'read_and_parse_travis_yml_file',
                    self._mock_read_travis_yml_file_fail)
        with dummy_path:
            actual_travis_script = (
                check_e2e_tests_are_captured_in_ci
                .get_e2e_suite_names_from_jobs_travis_yml_file())
        self.assertNotEqual(DUMMY_TEST_SUITES, actual_travis_script)

    def test_get_e2e_suite_names_from_protractor_file(self):
        dummy_path = self.swap(
            check_e2e_tests_are_captured_in_ci, 'read_protractor_conf_file',
            self._mock_read_protractor_conf_file)
        with dummy_path:
            actual_protractor_suites = (
                check_e2e_tests_are_captured_in_ci
                .get_e2e_suite_names_from_protractor_file())
        self.assertEqual(DUMMY_TEST_SUITES, actual_protractor_suites)

    def test_main_with_invalid_test_suites(self):
        def mock_get_e2e_suite_names_from_protractor_file():
            return ['fourWord', 'invalid', 'notPresent']

        mock_protractor_test_suites = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'get_e2e_suite_names_from_protractor_file',
            mock_get_e2e_suite_names_from_protractor_file)

        mock_tests_to_remove = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'TEST_SUITES_NOT_RUN_ON_TRAVIS',
            ['fourWord'])

        with mock_protractor_test_suites, mock_tests_to_remove:
            with self.assertRaisesRegexp(Exception,
                'Protractor test suites and Travis Ci test '
                'suites are not in sync.'):
                    check_e2e_tests_are_captured_in_ci.main()

    def test_main_with_invalid_travis_jobs_test_suite_length(self):
        travis_path_swap = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'read_and_parse_travis_yml_file',
            self._mock_read_travis_yml_file)

        mock_tests_to_remove = self._mock_tests_to_remove()

        mock_e2e_travis_jobs = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'get_e2e_suite_names_from_jobs_travis_yml_file',
            self._return_empty_list)

        with travis_path_swap, mock_tests_to_remove:
            with mock_e2e_travis_jobs:
                with self.assertRaisesRegexp(Exception,
                    'The e2e test suites that have been extracted from '
                    'jobs section from travis.ci are empty.'):
                        check_e2e_tests_are_captured_in_ci.main()

    def test_main_with_invalid_travis_script_test_suite_length(self):
        travis_path_swap = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'read_and_parse_travis_yml_file',
            self._mock_read_travis_yml_file)

        mock_tests_to_remove = self._mock_tests_to_remove()

        mock_e2e_travis_script = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'get_e2e_suite_names_from_script_travis_yml_file',
            self._return_empty_list)

        with travis_path_swap, mock_tests_to_remove:
            with mock_e2e_travis_script:
                with self.assertRaisesRegexp(Exception,
                    'The e2e test suites that have been extracted from '
                    'script section from travis.ci are empty.'):
                        check_e2e_tests_are_captured_in_ci.main()

    def test_main_with_invalid_protractor_test_suite_length(self):
        protractor_path_swap = self.swap(
            check_e2e_tests_are_captured_in_ci, 'read_protractor_conf_file',
            self._mock_read_protractor_conf_file)

        mock_tests_to_remove = self._mock_tests_to_remove()

        mock_e2e_test_suites = self.swap(
            check_e2e_tests_are_captured_in_ci,
            'get_e2e_suite_names_from_protractor_file',
            self._return_empty_list)

        with protractor_path_swap, mock_tests_to_remove:
            with mock_e2e_test_suites:
                with self.assertRaisesRegexp(Exception,
                    'The e2e test suites that have been extracted from '
                    'protractor.conf.js are empty.'):
                        check_e2e_tests_are_captured_in_ci.main()

    def test_main_without_errors(self):
        protractor_path_swap = self.swap(
            check_e2e_tests_are_captured_in_ci, 'read_protractor_conf_file',
            self._mock_read_protractor_conf_file)
        travis_path_swap = self.swap(
            check_e2e_tests_are_captured_in_ci, 'read_and_parse_travis_yml_file',
            self._mock_read_travis_yml_file)

        mock_tests_to_remove = self._mock_tests_to_remove()

        with protractor_path_swap, travis_path_swap, mock_tests_to_remove:
            check_e2e_tests_are_captured_in_ci.main()


TRAVIS_CI_DICT = {'env': {
'jobs': [
    'RUN_E2E_TESTS_ONEWORD=true', 'RUN_E2E_TESTS_TWO_WORDS=true']},
'script': [
    'if [ "RUN_E2E_TESTS_ONEWORD" == \'true\' ]; '
    'then travis_retry bash scripts/run_e2e_tests.sh'
    ' --suite="oneword" --prod_env; fi',
    'if [ "RUN_E2E_TESTS_TWO_WORDS" == \'true\' ]; '
    'then travis_retry bash scripts/run_e2e_tests.sh'
    ' --suite="twoWords" --prod_env; fi']}

DUMMY_PROTRACTOR_CONF_FILE = """var path = require('path')
var suites = {
  oneword: [
    'protractor/oneword.js'
  ],

  twoWords: [
    'protractor_desktop/twoWords.js'
  ]
};
"""