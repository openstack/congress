#!/usr/bin/env python
# Copyright (c) 2013 VMware, Inc. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
from congress.datasources.neutron_driver import NeutronDriver
from congress.tests import base
import logging
from mock import MagicMock


network_response = \
    {'networks':
        [{'status': 'ACTIVE',
          'subnets': ['4cef03d0-1d02-40bb-8c99-2f442aac6ab0'],
          'name': 'test-network',
          'provider:physical_network': None,
          'admin_state_up': True,
          'tenant_id': '570fe78a1dc54cffa053bd802984ede2',
          'provider:network_type': 'gre',
          'router:external': False,
          'shared': False,
          'id': '240ff9df-df35-43ae-9df5-27fae87f2492',
          'provider:segmentation_id': 4}]}


port_response = \
    {"ports":
        [{"status": "ACTIVE",
          "binding:host_id": "havana",
          "name": "",
          "allowed_address_pairs": [],
          "admin_state_up": True,
          "network_id": "240ff9df-df35-43ae-9df5-27fae87f2492",
          "tenant_id": "570fe78a1dc54cffa053bd802984ede2",
          "extra_dhcp_opts": [],
          "binding:vif_type": "ovs",
          "device_owner": "network:router_interface",
          "binding:capabilities": {"port_filter": True},
          "mac_address": "fa:16:3e:ab:90:df",
          "fixed_ips": [
              {"subnet_id": "4cef03d0-1d02-40bb-8c99-2f442aac6ab0",
               "ip_address": "90.0.0.1"}],
          "id": "0a2ce569-85a8-45ec-abb3-0d4b34ff69ba",
          "security_groups": [],
          "device_id": "864e4acf-bf8e-4664-8cf7-ad5daa95681e"}]}


class TestNeutronDriver(base.TestCase):

    def setUp(self):
        super(base.TestCase, self).setUp()
        self.neutron_client = MagicMock()
        self.network = network_response
        self.ports = port_response
        self.neutron_client.list_networks.return_value = self.network
        self.neutron_client.list_ports.return_value = self.ports
        self.driver = NeutronDriver()

    def test_list_networks(self):

        network_list = self.neutron_client.list_networks()
        network_tuple_list = \
            self.driver._get_tuple_list(network_list,
                                        self.driver.NEUTRON_NETWORKS)
        network_tuple = network_tuple_list[0]
        network_subnet_tuples = self.driver.network_subnet

        self.assertIsNotNone(network_tuple_list)
        self.assertEquals(1, len(network_tuple_list))
        self.assertEquals(1, len(network_subnet_tuples))

        key_to_index = self.driver.network_key_position_map()
        logging.info("key_to_index: " + str(key_to_index))
        logging.info("network: " + str(network_tuple))
        subnet_tuple_guid = network_tuple[key_to_index['subnets']]

        guid_key = network_subnet_tuples[0][0]
        guid_value = network_subnet_tuples[0][1]

        name = network_tuple[key_to_index['name']]
        status = network_tuple[key_to_index['status']]
        provider_physical_network = \
            network_tuple[key_to_index['provider:physical_network']]
        admin_state_up = network_tuple[key_to_index['admin_state_up']]
        tenant_id = network_tuple[key_to_index['tenant_id']]
        provider_network_type = \
            network_tuple[key_to_index['provider:network_type']]
        router_external = network_tuple[key_to_index['router:external']]
        shared = network_tuple[key_to_index['shared']]
        id = network_tuple[key_to_index['id']]
        provider_segmentation_id = \
            network_tuple[key_to_index['provider:segmentation_id']]

        self.assertEquals('ACTIVE', status)
        self.assertIsNotNone(subnet_tuple_guid)
        self.assertEqual(guid_key, subnet_tuple_guid)
        self.assertEqual('4cef03d0-1d02-40bb-8c99-2f442aac6ab0',
                         guid_value)
        self.assertEquals('test-network',
                          name)
        self.assertEquals(None, provider_physical_network)
        self.assertEquals('True', admin_state_up)
        self.assertEquals('570fe78a1dc54cffa053bd802984ede2',
                          tenant_id)
        self.assertEquals('gre', provider_network_type)
        self.assertEquals('False', router_external)
        self.assertEquals('False', shared)
        self.assertEquals('240ff9df-df35-43ae-9df5-27fae87f2492',
                          id)
        self.assertEquals(4, provider_segmentation_id)

    def test_list_ports(self):
        port_list = self.neutron_client.list_ports()
        port_tuple_list = \
            self.driver._get_tuple_list(port_list,
                                        self.driver.NEUTRON_PORTS)
        self.port_address_pairs = self.driver.port_address_pairs

        self.port_security_groups = self.driver.port_security_groups
        self.port_binding_capabilities = self.driver.port_binding_capabilities
        self.port_extra_dhcp_opts = self.driver.port_extra_dhcp_opts
        self.port_fixed_ips = self.driver.port_fixed_ips
        self.assertIsNotNone(port_tuple_list)
        self.assertEquals(1, len(port_tuple_list))

        # Input
        # [{"status": "ACTIVE",'+
        #    '"binding:host_id": "havana", "name": "",' +
        #    '"allowed_address_pairs": [],'+
        #    '"admin_state_up": True, ' +
        #    '"network_id": "240ff9df-df35-43ae-9df5-27fae87f2492",'+
        #    '"tenant_id": "570fe78a1dc54cffa053bd802984ede2",
        #     "extra_dhcp_opts": [],'+
        #    '"binding:vif_type": "ovs",' +
        #    '"device_owner": "network:router_interface",'+
        #    '"binding:capabilities": {"port_filter": True},' +
        #    '"mac_address": "fa:16:3e:ab:90:df",'+
        #    '"fixed_ips": [{"subnet_id":
        #    "4cef03d0-1d02-40bb-8c99-2f442aac6ab0",' +
        #    '"ip_address":"90.0.0.1"}],'+
        #    '"id": "0a2ce569-85a8-45ec-abb3-0d4b34ff69ba",
        #     "security_groups": [],'+
        #    '"device_id": "864e4acf-bf8e-4664-8cf7-ad5daa95681e"}]}')

        # Output
        # [('ACTIVE', 'havana', '', '90a579ea-ea45-11e3-a085-000c292422e8',
        #   'True',
        #   '240ff9df-df35-43ae-9df5-27fae87f2492',
        #   '570fe78a1dc54cffa053bd802984ede2',
        #   '90a5b5a4-ea45-11e3-a085-000c292422e8', 'ovs',
        #   'network:router_interface',
        #   '90a5f564-ea45-11e3-a085-000c292422e8', 'fa:16:3e:ab:90:df',
        #   '90a63222-ea45-11e3-a085-000c292422e8',
        #   '0a2ce569-85a8-45ec-abb3-0d4b34ff69ba',
        #   '90a6397a-ea45-11e3-a085-000c292422e8',
        #   '864e4acf-bf8e-4664-8cf7-ad5daa95681e')]

        status = port_tuple_list[0][0]
        binding_host_id = port_tuple_list[0][1]
        name = port_tuple_list[0][2]

        guid_allowed_address_pairs = port_tuple_list[0][3]
        guid_allowed_address_pairs_expected = self.port_address_pairs[0]

        admin_state_up = port_tuple_list[0][4]
        network_id = port_tuple_list[0][5]
        tenant_id = port_tuple_list[0][6]
        guid_extra_dhcp_opts = port_tuple_list[0][7]
        guid_extra_dhcp_opts_expected = self.port_extra_dhcp_opts[0][0]
        extra_dhcp_opts_value_actual = self.port_extra_dhcp_opts[0][1]

        binding_vif_type = port_tuple_list[0][8]
        device_owner = port_tuple_list[0][9]

        guid_binding_capabilities = port_tuple_list[0][10]
        guid_binding_capabilities_expected = \
            self.port_binding_capabilities[0][0]
        binding_capabilities_key_actual = self.port_binding_capabilities[0][1]
        binding_capabilities_value_actual = \
            self.port_binding_capabilities[0][2]

        mac_address = port_tuple_list[0][11]
        guid_fixed_ips = port_tuple_list[0][12]
        guid_fixed_ips_expected = self.port_fixed_ips[0][0]
        fixed_ips_key_one = self.port_fixed_ips[0][1]
        fixed_ips_value_one = self.port_fixed_ips[0][2]
        fixed_ips_key_two = self.port_fixed_ips[1][1]
        fixed_ips_value_two = self.port_fixed_ips[1][2]

        id = port_tuple_list[0][13]
        guid_security_groups = port_tuple_list[0][14]
        guid_security_groups_expected = self.port_security_groups[0][0]
        security_groups_value = self.port_security_groups[0][1]
        device_id = port_tuple_list[0][15]

        self.assertEqual('ACTIVE', status)
        self.assertEqual('havana', binding_host_id)
        self.assertEqual('', name)
        self.assertEqual(guid_allowed_address_pairs_expected[0],
                         guid_allowed_address_pairs)

        self.assertEqual(1, len(self.port_address_pairs))
        self.assertEqual('', self.port_address_pairs[0][1])
        self.assertEqual('True', admin_state_up)
        self.assertEqual('240ff9df-df35-43ae-9df5-27fae87f2492', network_id)
        self.assertEqual('570fe78a1dc54cffa053bd802984ede2', tenant_id)

        self.assertEqual(guid_extra_dhcp_opts_expected, guid_extra_dhcp_opts)
        self.assertEqual(1, len(self.port_extra_dhcp_opts))
        self.assertEqual('', extra_dhcp_opts_value_actual)

        self.assertEqual(guid_binding_capabilities_expected,
                         guid_binding_capabilities)
        self.assertEqual(1, len(self.port_binding_capabilities))
        self.assertEqual('port_filter', binding_capabilities_key_actual)
        self.assertEqual('True', binding_capabilities_value_actual)

        self.assertEqual('ovs', binding_vif_type)
        self.assertEqual('network:router_interface', device_owner)

        #    '"fixed_ips": [{"subnet_id":
        #    "4cef03d0-1d02-40bb-8c99-2f442aac6ab0",' +
        #    '"ip_address":"90.0.0.1"}],'+
        self.assertEqual(guid_fixed_ips_expected, guid_fixed_ips)
        self.assertEqual(2, len(self.port_fixed_ips))
        self.assertEqual('subnet_id', fixed_ips_key_one)
        self.assertEqual('4cef03d0-1d02-40bb-8c99-2f442aac6ab0',
                         fixed_ips_value_one)
        self.assertEqual('ip_address', fixed_ips_key_two)
        self.assertEqual('90.0.0.1', fixed_ips_value_two)

        self.assertEqual('fa:16:3e:ab:90:df', mac_address)
        self.assertEqual('0a2ce569-85a8-45ec-abb3-0d4b34ff69ba', id)

        self.assertEqual(guid_security_groups_expected,
                         guid_security_groups)
        self.assertEqual(1, len(self.port_security_groups))
        self.assertEqual('', security_groups_value)

        self.assertEqual('864e4acf-bf8e-4664-8cf7-ad5daa95681e', device_id)
