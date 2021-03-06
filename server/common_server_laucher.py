#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
from time import sleep
import logging
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.server.TNonblockingServer import TNonblockingServer


def start_server_handle(server_name, server_ip, port,
                        service_inter_module_name, service_inter_class_name,
                        service_impl_module_name, service_impl_class_name):
    """ start thrift server on port
    """

    # dynamic generate service impl and inter class
    AlgServiceImplClass = getattr(
        __import__(service_impl_module_name, globals(), locals(),
                   [service_impl_class_name]), service_impl_class_name)
    AlgServiceProcessorClass = getattr(
        __import__(service_inter_module_name, globals(), locals(),
                   [service_inter_class_name]), service_inter_class_name)

    # instantiation class object
    alg_service_processor = AlgServiceProcessorClass(AlgServiceImplClass(port))

    transport = TSocket.TServerSocket(server_ip, port)
    # tfactory = TTransport.TFramedTransportFactory()
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # server = TNonblockingServer(
    #     alg_service_processor, transport, tfactory, pfactory)
    server = TServer.TThreadPoolServer(alg_service_processor, transport,
                                       tfactory, pfactory)

    logging.info('Starting the %s server on IP %s port:%s', server_name,
                 server_ip, port)
    server.serve()


def load_server_config_and_start(
        server_name, server_ip, server_port_range, service_inter_module_name,
        service_inter_class_name, service_impl_module_name,
        service_impl_class_name):

    # get port range
    port_range = server_port_range.split('-')
    port_begin = int(port_range[0])
    port_end = int(port_range[1])
    # start servers
    for port in range(port_begin, port_end + 1):

        server_process = multiprocessing.Process(
            target=start_server_handle,
            args=(server_name, server_ip, port, service_inter_module_name,
                  service_inter_class_name, service_impl_module_name,
                  service_impl_class_name))
        server_process.start()
        sleep(0.2)  # delay starting to avoid console-print exception
