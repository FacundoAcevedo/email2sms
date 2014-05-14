#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Facundo M. Acevedo <acv2facundo[AT]gmail[DOT]com>
#
# Distributed under terms of the GPLv3+ license.

import email2sms


mail = email2sms.Email2sms()
mail.conectar()
mail.obtenerCorreos()
mail.procesarCorreos()

