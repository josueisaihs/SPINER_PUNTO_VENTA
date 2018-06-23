import sys, logging, os

__author__ = 'Josue Isai Hernandez'
__company__ = 'ElijoSoft DeskTech'
__email__ = 'josueisaihs@gmail.com'
__date__ = '19/08/2017'

logging.basicConfig(filename=os.path.join("system", "log", "logging.log"),
                        format='%(asctime)s\n\t%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
try:
    if sys.version == '3.6.0 |Anaconda 4.3.1 (64-bit)| (default, Dec 23 2016, 11:57:41) [MSC v.1900 64 bit (AMD64)]':
        import base64, datetime, re
        from PyQt5 import uic
        from PyQt5.Qt import Qt
        from PyQt5.QtCore import QSize, QTimer
        from PyQt5.QtGui import QIcon, QContextMenuEvent
        from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog, QListWidgetItem, QDialog, \
            QFileDialog, QTreeWidgetItem, QAction, QMenu
        import sqlite3 as sql
        from shutil import copyfile as cf
        import imghdr
        from hashlib import blake2s
        from hmac import compare_digest
        import xml.etree.ElementTree as et
        from platform import uname

        with open(os.path.join('system', 'layout', 'style.qss'), 'r') as stylefile:
            style = stylefile.read()
            stylefile.close()


        class SQL:
            def __init__(self):
                super(SQL, self).__init__()
                self.cnxn = sql.connect(os.path.join("system", "data", "dataBase.sqlite3"))
                self.db0 = self.cnxn.cursor()

            def loginUser(self, user, pwd):
                user = str(base64.b64encode(base64.b64encode(bytes(user, 'UTF-8'))))[2:-1]
                pwd = str(base64.b64encode(base64.b64encode(bytes(pwd, 'UTF-8'))))[2:-1]

                try:
                    user, type, name, lastname = self.userQuery("user, status, name, last_name",
                                                                " AND user == '{}' AND pwd == '{}'".format(user, pwd))[0]
                    user = str(base64.b64decode(base64.b64decode(bytes(user, 'UTF-8'))))[2:-1]
                except TypeError:
                    user, type, name, lastname = False, False, False, False

                return user, type, name, lastname

            def userInsert(self, user):
                self.db0.execute("INSERT OR IGNORE INTO Users(user, pwd, pin, status, name, last_name) "
                                 "VALUES (?, ?, ?, ?, ?, ?)", user.__sql__())
                self.commit()
                return self.db0.lastrowid != 0

            def factoryQuery(self, SELECT="DISTINCT supplier", QUERY=""):
                # self.db0.execute("SELECT {} FROM Factorys WHERE id != 0 {}".format(SELECT, QUERY))
                self.db0.execute("SELECT {} FROM Classify WHERE id != 0 {}".format(SELECT, QUERY))
                return self.db0.fetchall()

            def factoryInsert(self, text):
                self.db0.execute("INSERT OR IGNORE INTO Factorys(factory) VALUES (?)", [text])
                self.commit()
                return self.db0.lastrowid != 0

            def componetsQuery(self, SELECT="component", QUERY=""):
                self.db0.execute("SELECT {} FROM Components WHERE id != 0 {} ORDER BY component ASC".format(SELECT, QUERY))
                return self.db0.fetchall()

            def componentInsert(self, text):
                self.db0.execute("INSERT OR IGNORE INTO Components(component) VALUES (?)", [text])
                self.commit()
                return self.db0.lastrowid != 0

            def componentUpdate(self, textNew, textOld):
                self.db0.execute("UPDATE Components SET component = '{}' WHERE component == '{}'".
                                 format(textNew, textOld))
                self.commit()

            def componentDelete(self, text):
                self.db0.execute("SELECT id FROM Components WHERE component == '{}'".format(text))
                id_component = self.db0.fetchone()[0]
                id_classify = ""
                for i in self.db0.execute("SELECT id FROM Classify WHERE id_component == {}".format(id_component)):
                    id_classify += " OR id_classify == {}".format(i[0])
                id_classify = id_classify[4:]
                posible = self.classifyDelete(id_classify)
                if posible:
                    if id_classify != "":
                        self.db0.execute("DELETE FROM Classify WHERE {}".format(id_classify))
                        self.commit()
                    self.db0.execute("DELETE FROM Components WHERE component == '{}'".format(text))
                    self.commit()
                return posible

            def supplierDelete(self, text):
                id_classify = ""
                for i in self.db0.execute("SELECT id FROM Classify WHERE supplier == '{}'".format(text)):
                    id_classify += " OR id_classify == {}".format(i[0])
                id_classify = id_classify[4:]
                posible = self.classifyDelete(id_classify)
                if posible:
                    if id_classify != "":
                        id_classify = id_classify.replace("id_classify", "id")
                        self.db0.execute("DELETE FROM Classify WHERE {}".format(id_classify))
                        self.commit()
                return posible

            def classifyDelete(self, id_classify):
                posible = True

                if id_classify != "":
                    for i in self.db0.execute("SELECT * FROM ClassifySales WHERE {}".format(id_classify)):
                        posible = False
                        break

                    for i in self.db0.execute("SELECT * FROM ClassifyKardex WHERE {}".format(id_classify)):
                        posible = False
                        break

                    for i in self.db0.execute("SELECT * FROM ClassifyMake WHERE {}".format(id_classify)):
                        posible = False
                        break
                return posible

            def classifyQuery(self, SELECT="", QUERY=""):
                self.db0.execute("SELECT {} FROM Classify, Components WHERE Classify.id_component == Components.id {};".
                                 format(SELECT, QUERY))
                return self.db0.fetchall()

            def classifyInsert(self, product):
                self.db0.execute("SELECT id FROM Components WHERE component == '{}'".format(product[0].get_category()))
                id_component = self.db0.fetchone()[0]

                newClassify = [product[0].get_codCom(), product[0].get_codFab(), product[0].get_detail(), product[0].get_price1(),
                                product[0].get_price2(), product[0].get_price3(), product[0].get_price4(), product[0].get_cantAlm(),
                                product[0].get_supplier(), product[0].get_costProd(), product[0].get_cantMin(), product[0].get_location(),
                                id_component, product[0].get_tax(), product[0].get_cantVisit(), product[0].get_flete()]

                self.db0.execute(
                    "INSERT INTO Classify(codeCom, codeFab, detail, price1, price2, price3, price4, cantAlm, "
                    "supplier, costProd, cantMin, location, id_component, tax, cantVisit, flete) VALUES "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", newClassify)

                self.commit()

                return self.db0.lastrowid != 0

            def classifyUpdate(self, product, concept=""):
                self.db0.execute("UPDATE Classify SET price1 = {p1}, price2 = {p2}, price3 = {p3}, price4 = {p4},"
                                 "cantAlm = {cA}, costProd = {cP}, location = '{l}', cantMin = {cM}, tax = {t}, "
                                 "flete = {f}, detail == '{d}' WHERE id IN "
                                 "(SELECT id FROM Classify WHERE codeCom == '{i}')".
                                 format(p1=product[0].get_price1(), p2=product[0].get_price2(), p3=product[0].get_price3(),
                                        p4=product[0].get_price4(), cA=product[0].get_cantAlm(), cP=product[0].get_costProd(),
                                        l=product[0].get_location(), cM=product[0].get_cantMin(), t=product[0].get_tax(),
                                        f=product[0].get_flete(), i=product[0].get_codCom(), d=product[0].get_detail()))
                self.commit()

            def supplierUpdate(self, textNew, textOld):
                self.db0.execute("UPDATE Classify SET supplier = '{}' WHERE supplier == '{}'".format(textNew, textOld))
                self.commit()

            def makeQuery(self, SELECT="Ma.make, Mo.model, Cm.year, Mo.engine", QUERY=""):
                self.db0.execute("SELECT {} FROM Makes Ma, Models Mo, ClassifyMake Cm, Classify C "
                                 "WHERE Cm.id_models == Mo.id AND Mo.id_make == Ma.id AND Cm.id_classify == C.id {}".
                                 format(SELECT, QUERY))
                return self.db0.fetchall()

            def makeInsert(self, make):
                self.db0.execute("INSERT OR IGNORE INTO Makes(make) VALUES (?)", [make])
                self.commit()

                return self.db0.lastrowid != 0

            def modelInsert(self, model):
                self.db0.execute("SELECT id FROM Makes WHERE make == '{}'".format(model[0]))
                id_make = self.db0.fetchone()[0]

                self.db0.execute("INSERT OR IGNORE INTO Models(id_make, model, engine) VALUES (?, ?, ?)",
                                 [id_make, model[1], model[2]])
                self.commit()

                return self.db0.lastrowid != 0

            def spinerSearchQuery(self, SELECT, QUERY_CLASSIFY, QUERY_MAKE, LIMIT=250):
                classify = []
                if QUERY_CLASSIFY != "":
                    self.db0.execute("SELECT {} FROM Classify C, Components Co WHERE "
                                     "C.id_component == Co.id {} GROUP BY C.id ORDER BY C.cantVisit DESC LIMIT {}".
                                     format(SELECT, QUERY_CLASSIFY, LIMIT))

                    classify = self.db0.fetchall()

                make = []
                if QUERY_MAKE != "":
                    self.db0.execute("SELECT {} FROM Classify C, Components Co, Makes Ma, Models Mo, ClassifyMake Cm WHERE "
                                     "C.id_component == Co.id AND Ma.id == Mo.id_make AND Mo.id == Cm.id_models "
                                     "AND Cm.id_classify == C.id {} GROUP BY C.id ORDER BY C.cantVisit DESC LIMIT {}".
                                     format(SELECT, QUERY_MAKE, LIMIT))

                    make = self.db0.fetchall()

                result = []
                result.extend(classify)
                result.extend(make)
                return result

            def kardexClassifyQuery(self, SELECT="El.time, Co.component, C.codeFab, C.codeCom, Ck.newCant, C.costProd, "
                                                 "round(-C.costProd * Ck.newCant, 2), "
                                                 "round(Ck.newCant * max(C.price1, C.price2, C.price3, C.price4), 2)",
                                    QUERY="GROUP BY Ck.id_invoice"):
                self.db0.execute("SELECT {} FROM Classify C, Components Co, ClassifyKardex Ck, Invoices I, EventsLog El "
                                 "WHERE Ck.id_classify == C.id AND Ck.id_invoice == I.id AND I.id_event == El.id_event "
                                 "AND C.id_component == Co.id {}".format(SELECT, QUERY))

                kardex = Kardex()
                for i in self.db0.fetchall():
                    kardexDetalle = KardexDetalle()
                    kardexDetalle.fecha = i[0]
                    kardexDetalle.category = i[1]
                    kardexDetalle.codFab = i[2]
                    kardexDetalle.codCom = i[3]
                    kardexDetalle.kardex = i[4]
                    kardexDetalle.costProd = i[5]
                    kardexDetalle.kardexCosto = i[6]
                    kardexDetalle.kardexCotizacion = i[7]

                    kardex.addKardex(kardexDetalle)
                    kardex.kardexDetalleClass = kardexDetalle

                return kardex

            def salesClassifyQuery(self, SELECT="El.time, Co.component, C.codeFab, C.codeCom, Cs.cant, C.costProd, "
                                                "round(-Cs.cant * C.costProd, 2), "
                                                "Cs.price, round(Cs.cant * (Cs.price - C.costProd), 2), "
                                                "round(Cs.cant * Cs.price, 2)",
                                   QUERY="GROUP BY Cs.id_classify"):

                self.db0.execute("SELECT {} FROM Classify C, Components Co, ClassifySales Cs, Invoices I, EventsLog El "
                                 "WHERE Cs.id_classify == C.id AND Cs.id_invoice == I.id AND I.id_event == El.id_event "
                                 "AND C.id_component == Co.id {}".format(SELECT, QUERY))

                return self.db0.fetchall()

            def kardexQuery(self, SELECT="round(sum(K.total), 2)", QUERY=""):
                self.db0.execute("SELECT {} FROM Kardex K, Invoices I, EventsLog El "
                                 "WHERE K.id_invoice == I.id AND I.id_event == El.id_event {}".
                                 format(SELECT, QUERY))
                kardex = self.db0.fetchone()[0]
                if not kardex:
                    kardex = 0.0
                return kardex

            def salesQuery(self, SELECT="El.time, 'Sales', Cs.cant", QUERY=""):
                self.db0.execute("SELECT {} FROM Classify C, ClassifySales Cs, Invoices I, EventsLog El "
                                 "WHERE Cs.id_classify == C.id AND Cs.id_invoice == I.id AND I.id_event == El.id_event {} "
                                 "ORDER BY El.time DESC".format(SELECT, QUERY))

                return self.db0.fetchall()

            def classifyMakeInsert(self, make):
                self.db0.execute("SELECT id FROM Classify WHERE codeCom == '{}'".format(make[0]))
                id_classify = self.db0.fetchone()[0]

                self.db0.execute("SELECT Models.id FROM Models, Makes WHERE Makes.make == '{}' AND Models.model == '{}' AND "
                                 "Makes.id == Models.id_make".format(make[1], make[2]))
                id_models = self.db0.fetchone()[0]

                self.db0.execute("INSERT OR IGNORE INTO ClassifyMake (id_classify, year, id_models) VALUES (?, ?, ?)",
                                 [id_classify, make[3], id_models])
                self.commit()

                return self.db0.lastrowid != 0

            def clientQuery(self, SELECT="", QUERY=""):
                self.db0.execute("SELECT {} FROM Clients WHERE id != 0 {} ".format(SELECT, QUERY))
                return self.db0.fetchall()

            def clientInsert(self, client):
                self.db0.execute("INSERT OR IGNORE INTO Clients(client, address, phone, email, discount) VALUES (?, ?, ?, ?, ?)",
                                 client)
                self.commit()
                return self.db0.lastrowid != 0

            def finanzasQuery(self, fecha):
                finanzas = Finanzas()
                # Kardex
                kardex = self.queryFree(SELECT="El.time, I.type, Co.component, C.codeCom, C.codeFab, Ck.newCant, "
                                               "round(-Ck.newCant * C.costProd, 2)",
                                        FROM="EventsLog El, Invoices I, Components Co, Classify C, ClassifyKardex Ck",
                                        QUERY="Ck.id_invoice == I.id AND I.id_event == El.id_event AND Ck.id_classify == C.id "
                                              "AND C.id_component == Co.id AND El.time >= '{} 00:00:00' AND El.time <= '{} 23:59:59' GROUP BY I.id".
                                        format(fecha[0], fecha[1]))
                for i in kardex:
                    invoiceKardex = InvoiceKardex()
                    invoiceKardex.fecha = i[0]
                    invoiceKardex.invoice = i[1]
                    invoiceKardex.set_category(i[2])
                    invoiceKardex.set_codCom(i[3])
                    invoiceKardex.set_codFab(i[4])
                    invoiceKardex.kardex = i[5]
                    invoiceKardex.kardexCosto = i[6]

                    finanzas.addConceptoKardex(invoiceKardex)

                # Venta
                sales = self.queryFree(SELECT="El.time, I.type, Co.component, C.codeCom, C.codeFab, Cs.cant, "
                                              "round(-Cs.cant * C.costProd, 2), round(Cs.cant * (Cs.price - C.costProd), 2), Cl.client",
                                       FROM="EventsLog El, Invoices I, Components Co, Classify C, ClassifySales Cs, Sales S, Clients Cl",
                                       QUERY="Cs.id_invoice == I.id AND I.id_event == El.id_event AND Cs.id_classify == C.id AND S.id_invoice == Cs.id_invoice AND S.id_client == Cl.id "
                                              "AND C.id_component == Co.id AND El.time >= '{} 00:00:00' AND El.time <= '{} 23:59:59' GROUP BY I.id".
                                        format(fecha[0], fecha[1]))
                for i in sales:
                    finanzasSales = finanzas.Sales()
                    finanzasSales.fecha = i[0]
                    finanzasSales.invoice = i[1]
                    finanzasSales.producto.set_category(i[2])
                    finanzasSales.producto.set_codCom(i[3])
                    finanzasSales.producto.set_codFab(i[4])
                    finanzasSales.sale = i[5]
                    finanzasSales.haber = i[6]
                    finanzasSales.debe = i[7]
                    finanzasSales.client = i[8]

                    finanzas.addConceptoSales(finanzasSales)

                discount = self.queryFree(SELECT="El.time, I.type, Cl.client, -S.discount, round(S.discount * 100 / S.total, 2)",
                                          FROM="EventsLog El, Invoices I, Sales S, Clients Cl",
                                          QUERY="S.id_invoice == I.id AND I.id_event == El.id_event AND S.id_client == Cl.id "
                                                "AND S.discount > 0 AND El.time >= '{} 00:00:00' AND El.time <= '{} 23:59:59' GROUP BY I.id".
                                        format(fecha[0], fecha[1]))
                for i in discount:
                    finanzasDiscount = finanzas.Discount()
                    finanzasDiscount.fecha = i[0]
                    finanzasDiscount.invoice = i[1]
                    finanzasDiscount.client = i[2]
                    finanzasDiscount.discount = i[3]
                    finanzasDiscount.porciento = i[4]

                    finanzas.addConceptoDiscount(finanzasDiscount)

                debt = self.queryFree(SELECT="El.time, I.type, Cl.client, round(-D.dep + D.money, 2), "
                                             "round(D.money * 100 / D.dep)",
                                      FROM="EventsLog El, Invoices I, Debt D, Clients Cl",
                                      QUERY="D.id_invoice == I.id AND I.id_event == El.id_event AND D.money < D.dep AND D.id_client == Cl.id AND El.time >= '{} 00:00:00' AND El.time <= '{} 23:59:59' GROUP BY I.id".
                                        format(fecha[0], fecha[1]))
                for i in debt:
                    finanzasDebt = finanzas.Debt()
                    finanzasDebt.fecha = i[0]
                    finanzasDebt.invoice = i[1]
                    finanzasDebt.client = i[2]
                    finanzasDebt.debt = i[3]
                    finanzasDebt.pagado = i[4]

                    finanzas.addConceptoDebt(finanzasDebt)

                return finanzas

            def queryFree(self, SELECT="", FROM="", QUERY=""):
                self.db0.execute("SELECT {} FROM {} WHERE {}".format(SELECT, FROM, QUERY))

                return self.db0.fetchall()

            def userQuery(self, SELECT="id", QUERY=""):
                self.db0.execute("SELECT {} FROM Users WHERE id != 0 {}".format(SELECT, QUERY))
                return self.db0.fetchall()

            def invoiceSalesInsert(self, invoice):
                id_user = self.userQuery(QUERY="AND user == '{}'".format(
                    str(base64.b64encode(base64.b64encode(bytes(invoice.user, 'UTF-8'))))[2:-1]))[0][0]
                id_event = self.eventInsert([id_user, 'Sales Invoice', '-'])

                self.db0.execute("INSERT INTO Invoices(id_event, type) VALUES (?, ?)", [id_event, invoice.invoice])
                self.commit()

                id_invoice = self.db0.lastrowid

                for i in range(invoice.classifySales.__len__()):
                    invoice.classifySales[i].insert(0, id_invoice)

                self.db0.executemany("INSERT INTO ClassifySales(id_invoice, id_classify, cant, price) VALUES (?, ?, ?, ?)",
                                     invoice.classifySales)
                self.commit()

                self.db0.execute("INSERT INTO Sales(id_invoice, id_client, discount, debt, total) VALUES (?, ?, ?, ?, ?)",
                                 [id_invoice,
                                  self.clientQuery(SELECT="id", QUERY=" AND client == '{}'".format(invoice.get_name()))[0][0],
                                  invoice.descuento, invoice.deuda, invoice.total])
                self.commit()

                if invoice.deuda > 0:
                    self.db0.execute("INSERT INTO Debt(id_invoice, id_client, money, dep) VALUES (?, ?, ?, ?)",
                                     [id_invoice,
                                      self.clientQuery(SELECT="id", QUERY=" AND client == '{}'".format(invoice.get_name()))[0][0],
                                      0, invoice.deuda])
                    self.commit()

            def invoiceKardexInsert(self, invoice):
                id_user = self.userQuery(QUERY="AND user == '{}'".format(
                    str(base64.b64encode(base64.b64encode(bytes(invoice.user, 'UTF-8'))))[2:-1]))[0][0]
                id_event = self.eventInsert([id_user, 'Kardex Invoice', '-'])

                self.db0.execute("INSERT INTO Invoices(id_event, type) VALUES (?, ?)", [id_event, invoice.invoice])
                self.commit()

                id_invoice = self.db0.lastrowid

                invoice.id_invoice = id_invoice

                self.db0.executemany("INSERT INTO Kardex(id_invoice, tax, total) VALUES (?, ?, ?)",
                                     [invoice.getKardexSQL()])
                self.commit()

                self.db0.execute("INSERT INTO ClassifyKardex(id_invoice, id_classify, newCant) VALUES (?, ?, ?)",
                                 invoice.getKardexDetalleSQL())
                self.commit()

            def debtQuery(self, SELECT="I.type, C.client, D.money, D.dep, El.time", QUERY=""):
                self.db0.execute("SELECT {} FROM Debt D, Clients C, Invoices I, EventsLog El WHERE I.id == D.id_invoice AND D.dep > D.money "
                                 "AND C.id == D.id_client AND I.id_event == El.id_event {}".
                                 format(SELECT, QUERY))
                lista = []
                for i in self.db0.fetchall():
                    dept = DebtDetalle()
                    dept.invoice = i[0]
                    dept.client = i[1]
                    dept.money = i[2]
                    dept.dep = i[3]
                    dept.date = i[4]
                    lista.append(dept)
                return lista

            def debtUpdate(self, debt):
                self.db0.execute("SELECT id FROM Invoices WHERE type == '{}'".format(debt.invoice))
                id_invoice = self.db0.fetchone()[0]

                self.db0.execute("SELECT id FROM Clients WHERE client == '{}'".format(debt.client))
                id_client = self.db0.fetchone()[0]

                self.db0.execute("UPDATE Debt SET money = {money} WHERE id_invoice == {id_invoice} "
                                 "AND id_client == {id_client}".
                                 format(id_invoice=id_invoice, id_client=id_client, money=debt.money))
                self.commit()

            def workerInsert(self, worker):
                self.db0.execute("INSERT OR IGNORE INTO Workers(name, lastname, ci, street, city, state, phone, "
                                 "phoneOther, mobil, mobilOther, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 worker.getSQL())
                self.commit()

                return self.db0.lastrowid

            def eventInsert(self, event):
                self.db0.execute("INSERT INTO Events(id_user, event, operation) VALUES (?, ?, ?)", event)

                self.commit()

                return self.db0.lastrowid

            def eventQuery(self, SELECT="id", QUERY=""):
                self.db0.execute("SELECT {} FROM Events WHERE id != 0 {}".format(SELECT, QUERY))

                return self.db0.fetchone()[0]

            def sequenceQuery(self, SELECT="", QUERY=""):
                self.db0.execute("SELECT {} FROM sqlite_sequence WHERE name GLOB '*' {}".format(SELECT, QUERY))
                return self.db0.fetchone()

            def commit(self):
                self.cnxn.commit()

            def close(self):
                self.close()
        # <> fin SQL

        class ElijoSoftSecure:
            def __init__(self):
                super(ElijoSoftSecure, self).__init__()

                # Creando archivos de Escritura
                dir = "Microsoft ES"
                self.path = os.path.join("system", "ProgramData", dir)
                try:
                    os.mkdir(self.path)
                    list = os.listdir(os.path.join("system", "ProgramData"))
                    if dir in list:
                        fileCreado = True
                    else:
                        fileCreado = False
                except FileExistsError as e:
                    fileCreado = True

                if fileCreado:
                    self.fileRequest = open(os.path.join(self.path, "{}.es".format(self.genCode("request"))), "r+")
                    self.fileLicence = open(os.path.join(self.path, "{}.es".format(self.genCode("licence"))), "r+")
                    self.fileDate = open(os.path.join(self.path, "{}.es".format(self.genCode("date"))), "r+")

            def loadFiles(self):
                self.fileRequest = open(os.path.join(self.path, "{}.es".format(self.genCode("request"))), "r+")
                self.fileLicence = open(os.path.join(self.path, "{}.es".format(self.genCode("licence"))), "r+")
                self.fileDate = open(os.path.join(self.path, "{}.es".format(self.genCode("date"))), "r+")

            def genCode(self, valor, key=b"pTmABMWldKQriUvg"):
                hash = blake2s(bytes(valor, "UTF-8"), key=key, digest_size=16)
                return hash.hexdigest()

            def formatCode(self, valor, key=b"pTmABMWldKQriUvg"):
                count = 0
                sal = ""
                for i in self.genCode(valor, key=key):
                    if count < 3:
                        sal += i
                        count += 1
                    else:
                        sal += i + "-"
                        count = 0
                sal = sal[:-1]
                return sal

            def comparaDigest(self, valor1, valor2):
                return compare_digest(valor1, valor2)

            def iterador(self, encabezado, lista):
                valor = "{}".format(encabezado)
                for i in lista:
                    valor += " {}".format(i)
                return valor

            def filtre(self, valor):
                if "-" in valor:
                    valor = valor.replace("-", "")

                return valor

            def decodeDate(self, hourRef, formatDate=False):
                rango = {True: 8761, False: 367}
                for i in range(rango[formatDate]):
                    if not formatDate:
                        fecha = "{}".format(datetime.date.today() - datetime.timedelta(days=i))
                    else:
                        fecha = datetime.datetime.today() - datetime.timedelta(hours=i)
                        fecha = "{}".format(fecha.isoformat(' ', timespec='hours'))

                    if self.comparaDigest(hourRef, self.genCode(fecha)):
                        return True, fecha
                return False, 0

            def genRequest(self, format=False, k=0, forLic=False):
                __PLATFORM__ = self.iterador("__PLATFORM__:", uname())
                __DATE__ = "__DATE__: {}".format(datetime.date.today() - datetime.timedelta(days=k))

                if forLic:
                    writeRequest = self.write(self.fileRequest,
                                              "{}g{}".format(self.genCode("{}".format(datetime.date.today())),
                                                             self.genCode("{} {}".format(__PLATFORM__, __DATE__))),
                                              True)

                if format:
                    return self.formatCode("{} {}".format(__PLATFORM__, __DATE__))
                else:
                    return self.genCode("{} {}".format(__PLATFORM__, __DATE__))

            def findRequest(self, requestRef="", dias=367):
                requestRef = self.filtre(requestRef)
                for i in range(dias):
                    if self.comparaDigest(requestRef, self.genRequest(k=i)):
                        return True, i
                return False, 0

            def validRequest(self):
                request = self.read(self.fileRequest)
                if request != ['']:
                    request = request[-2]
                    return True
                else:
                    return False

            def verifRequest(self, forLic=False, requestRef=""):
                if forLic:
                    return self.findRequest(requestRef, 4)
                else:
                    return self.findRequest(requestRef)

            def registreLic(self, licenceRef):
                licenceRef = self.filtre(licenceRef)
                is_valid, dias = self.verifLicence(licenceRef)
                if is_valid:
                    writeLicence = self.write(self.fileLicence,
                                              "{}g{}".format(self.genCode("{}".format(datetime.date.today())),
                                                             licenceRef), True)
                    if writeLicence:
                        return True, dias
                    else:
                        return False, 0
                else:
                    return False, -1

            def validLic(self):
                text = self.read(self.fileLicence)
                if text != [""]:
                    try:
                        fechaLicence, license = text[-2].split("g")
                        fechadecode = self.decodeDate(fechaLicence)

                        text = self.read(self.fileRequest)
                        try:
                            fechaRequest, request = text[-2].split("g")

                            is_valid, dias = self.verifLicence(license)

                            if is_valid and fechadecode[0] and fechaLicence == fechaRequest:
                                year, month, day = fechadecode[1].split("-")
                                fechafin = datetime.date(year=int(year), month=int(month),
                                                         day=int(day)) + datetime.timedelta(days=dias)
                                if fechafin >= datetime.date.today():
                                    tiempo = fechafin - datetime.date.today()
                                    return True, tiempo.days
                                else:
                                    tiempo = datetime.date.today() - fechafin
                                    return False, tiempo.days
                            else:
                                return False, -1
                        except ValueError as e:
                            logging.critical("Error Fatal en request split")
                            return False, -2
                    except ValueError as e:
                        logging.critical("Error Fatal en licence split")
                        return False, -3
                else:
                    return False, 0

            def write(self, file, text, textplain=False):
                if textplain:
                    if not self.existRegistro(file, text):
                        file.write(text)
                    else:
                        return False
                else:
                    if not self.existRegistro(file, self.genCode("{}".format(text))):
                        file.write(self.genCode("{}".format(text)))
                    else:
                        return False
                file.write("\n")
                return True

            def read(self, file):
                self.loadFiles()
                text = file.read().split("\n")
                return text

            def existRegistro(self, file, valor):
                text = self.read(file)
                return valor in text

            def genLic(self, request, dias, format=True, forLic=True):
                if dias <= 367:
                    if self.verifRequest(forLic=forLic, requestRef=request)[0]:
                        key = bytes(self.filtre(request), "UTF-8")
                        if format:
                            return self.formatCode("{}".format(dias), key=key)
                        else:
                            return self.genCode("{}".format(dias), key=key)
                    else:
                        return False, -1
                else:
                    return False, 0

            def verifLicence(self, licenceRef):
                licenceRef = self.filtre(licenceRef)
                requestRef = self.read(self.fileRequest)
                if requestRef != [""]:
                    try:
                        requestRef = requestRef[-2].split("g")[1]
                        if self.verifRequest(requestRef=requestRef)[0]:
                            for i in range(367):
                                if self.comparaDigest(licenceRef,
                                                      self.genLic(requestRef, i, format=False, forLic=False)):
                                    return True, i
                            return False, 0
                        else:
                            return False, -1
                    except ValueError as e:
                        logging.critical("Error Fatal request split 1")
                else:
                    return False, -2

            def validDate(self):
                fechaactual = datetime.datetime.today().isoformat(' ', timespec="hours")

                if not self.write(self.fileDate, fechaactual):
                    fechavieja = self.read(self.fileDate)[-2]
                    fechavieja = self.decodeDate(fechavieja, formatDate=True)
                    if fechavieja[0]:
                        year, month, day = fechavieja[1].split("-")
                        day, hour = day.split(" ")
                        fechavieja = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))
                        if fechavieja <= datetime.datetime.today():
                            return True, 0
                        else:
                            tiempo = fechavieja - datetime.datetime.today()
                            return False, tiempo.days
                    else:
                        return False, -1
                else:
                    return True, 0

            def validProgram(self):
                is_valid_licence, _ = self.validLic()
                is_valid_date, _ = self.validDate()

                return is_valid_date and is_valid_licence

            def verifLayout(self, dir, file):
                tree = et.parse(os.path.join(dir, file))
                root = tree.getroot()
                for child in root:
                    if child.tag == "widget":
                        if child.attrib["key"] == blake2s(bytes("{}".format(file), 'UTF-8'),
                                                          digest_size=16, key=b"pTmABMWldKQriUvg").hexdigest():
                            return True
                        else:
                            return False

            def end(self):
                self.fileDate.close()
                self.fileLicence.close()
                self.fileRequest.close()
        # <> fin ElijoSoftSecureClient

        masterSecure = ElijoSoftSecure()

        try:
            dir = os.path.join("system", "layout")
            i = 0

            if masterSecure.verifLayout(dir=dir, file="login.ui"):
                loginUi = uic.loadUiType(os.path.join("system", "layout", "login.ui"))[0]
            else:
                i += 1
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                loginUi = None

            if masterSecure.verifLayout(dir, "product.ui"):
                productUi = uic.loadUiType(os.path.join("system", "layout", "product.ui"))[0]
            else:
                i += 1
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                productUi = None

            if masterSecure.verifLayout(dir, "searcher.ui"):
                searcherUi = uic.loadUiType(os.path.join("system", "layout", "searcher.ui"))[0]
            else:
                i += 1
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                productUi = None

            if masterSecure.verifLayout(dir, "sales.ui"):
                salesUi = uic.loadUiType(os.path.join("system", "layout", "sales.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                salesUi = None

            if masterSecure.verifLayout(dir, "dialogOpcion.ui"):
                dialogOpcionUi = uic.loadUiType(os.path.join("system", "layout", "dialogOpcion.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogOpcionUi = None

            if masterSecure.verifLayout(dir, "dialogSelect.ui"):
                dialogSelectUi = uic.loadUiType(os.path.join("system", "layout", "dialogSelect.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogSelectUi = None

            if masterSecure.verifLayout(dir, "dialogMake.ui"):
                dialogMakeUi = uic.loadUiType(os.path.join("system", "layout", "dialogMake.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogMakeUi = None

            if masterSecure.verifLayout(dir, "dialogClient.ui"):
                dialogClientUi = uic.loadUiType(os.path.join("system", "layout", "dialogClient.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogClientUi = None

            if masterSecure.verifLayout(dir, "dialogNewClient.ui"):
                dialogNewClientUi = uic.loadUiType(os.path.join("system", "layout", "dialogNewClient.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogNewClientUi = None

            if masterSecure.verifLayout(dir, "dialogCar.ui"):
                dialogCarUi = uic.loadUiType(os.path.join("system", "layout", "dialogCar.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogCarUi = None

            if masterSecure.verifLayout(dir, "dialogPayment.ui"):
                dialogPaymentUi = uic.loadUiType(os.path.join("system", "layout", "dialogPayment.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogPaymentUi = None

            if masterSecure.verifLayout(dir, "inicio.ui"):
                inicioUi = uic.loadUiType(os.path.join("system", "layout", "inicio.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                inicioUi = None

            if masterSecure.verifLayout(dir, "dialogCalendar.ui"):
                dialogCalendarioUi = uic.loadUiType(os.path.join("system", "layout", "dialogCalendar.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogCalendarioUi = None

            if masterSecure.verifLayout(dir, "dialogFinanzas.ui"):
                dialogFinanzasUi = uic.loadUiType(os.path.join("system", "layout", "dialogFinanzas.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogFinanzasUi = None

            if masterSecure.verifLayout(dir, "dialogLic.ui"):
                dialogLicUi = uic.loadUiType(os.path.join("system", "layout", "dialogLic.ui"))[0]
            else:
                i += 0
                logging.warning("Problemas cargando el archivo %s", "FILE00{}".format(i))
                dialogLicUi = None

            dialogListUi = uic.loadUiType(os.path.join("system", "layout", "dialogList.ui"))[0]
            dialogAccountUi = uic.loadUiType(os.path.join("system", "layout", "account.ui"))[0]
            dialogNewWorker = uic.loadUiType(os.path.join("system", "layout", "dialogWorker.ui"))[0]
        except:
            logging.error("Problemas cargando archivos %s", 'EXCFILE001')

        del masterSecure


        class ProductDetalle:
            def __init__(self, id=0, codCom="", codFab="", detail="", price1=0.0, price2=0.0, price3=0.0, price4=0.0, cantAlm=0,
                         supplier="", costProd=0.0, cantMin=0, location="", category="", tax=0.0, cantVisit=0, flete=0.0,
                         barcode=""):
                self.id = id
                self.codCom = codCom
                self.codFab = codFab
                self.detail = detail
                self.price1 = price1
                self.price2 = price2
                self.price3 = price3
                self.price4 = price4
                self.cantAlm = cantAlm
                self.supplier = supplier
                self.costProd = costProd
                self.cantMin = cantMin
                self.location = location
                self.category = category
                self.tax = tax
                self.cantVisit = cantVisit
                self.flete = flete
                self.barcode = barcode
                self.disponibilidad = False
            # fin __init__

            def get_Id(self):
                return self.id
            # fin get_Id

            def set_Id(self, id):
                self.id = id
            # fin set_Id

            def set_codCom(self, codeCom):
                self.codCom = codeCom
            # fin set_codCom

            def get_codCom(self):
                return self.codCom
            # fin get_codCom

            def set_codFab(self, codeFab):
                self.codFab = codeFab
            # fin set_codFab

            def get_codFab(self):
                return self.codFab
            # fin get_codFab

            def set_detail(self, detail):
                self.detail = detail
            # fin set_detail

            def get_detail(self):
                return self.detail
            # fin get_detail

            def set_price1(self, price1):
                self.price1 = price1
            # fin set_price1

            def get_price1(self):
                return self.price1
            # fin get_price1

            def set_price2(self, price2):
                self.price2 = price2
            # fin set_price2

            def get_price2(self):
                return self.price2
            # fin get_price2

            def set_price3(self, price3):
                self.price3 = price3
            # fin set_

            def get_price3(self):
                return self.price3
            # fin get_price3

            def set_price4(self, price4):
                self.price4 = price4
            # fin set_price4

            def get_price4(self):
                return self.price4
            # fin get_price4

            def set_cantAlm(self, cantAlm):
                self.cantAlm = cantAlm
            # fin set_cantAlm

            def get_cantAlm(self):
                return self.cantAlm
            # fin get_cantAlm

            def set_supplier(self, supplier):
                self.supplier = supplier
            # fin set_supplier

            def get_supplier(self):
                return self.supplier
            # fin get_supplier

            def set_costProd(self, costProd):
                self.costProd = costProd
            # fin set_costProd

            def get_costProd(self):
                return self.costProd
            # fin get_costProd

            def set_cantMin(self, cantMin):
                self.cantMin = cantMin
            # fin set_cantMin

            def get_cantMin(self):
                return self.cantMin
            # fin get_cantMin

            def set_location(self, location):
                self.location = location
            # fin set_location

            def get_location(self):
                return self.location
            # fin get_location

            def set_category(self, category):
                self.category = category
            # fin set_category

            def get_category(self):
                return self.category
            # fin get_category

            def set_tax(self, tax):
                self.tax = tax
            # fin set_tax

            def get_tax(self):
                return self.tax
            # fin get_tax

            def set_cantVisit(self, cantVisit):
                self.cantVisit = cantVisit
            # fin set_cantVisit

            def get_cantVisit(self):
                return self.cantVisit
            # fin get_cantVisit

            def set_flete(self, flete):
                self.flete = flete
            # fin set_flete

            def get_flete(self):
                return self.flete
            # fin get_flete

            def set_barcode(self, barcode):
                self.barcode = barcode
            # fin set_barcode

            def get_barcode(self):
                return self.barcode
            # fin get_flete

            def get_WARN_PROD_LOW(self):
                return self.cantAlm < self.cantMin
            # fin get_WARN_PROD_LOW

            def get_Disponibilidad(self):
                return self.disponibilidad

            def set_Disponibilidad(self, dis):
                self.disponibilidad = dis

            def get_gananciaPerCapita(self):
                return self.price1 - self.costProd, self.price2 - self.costProd, self.price3 - self.costProd, \
                       self.price4 - self.costProd
            # fin get_utilidad

            def get_status(self):
                return self.codCom, self.cantAlm, self.price1, self.price2, self.price3, self.price4, self.cantVisit
            # fin get_status

            def get_update(self):
                return self.price1, self.price2, self.price3, self.price4, self.cantAlm, self.codFab, self.supplier, \
                       self.costProd, self.location, self.cantMin, self.tax, self.detail, self.flete, self.id
            # fin get_update

            def add_visit(self):
                self.cantVisit += 1
            # fin add_visit

            def add_cantAlm(self, cant):
                self.cantAlm += float(cant)
            # fin add_cantAlm
        # <> fin ProductDetalle


        class Cliente:
            def __init__(self):
                self.name = ""
                self.address = ""
                self.phone = ""
                self.email = ""
                self.discount = ""

            def get_name(self):
                return self.name

            def set_Name(self, name):
                self.name = name

            def get_address(self):
                return self.address

            def set_Address(self, address):
                self.address = address

            def get_phone(self):
                return self.phone

            def set_Phone(self, phone):
                self.phone = phone

            def get_email(self):
                return self.email

            def set_Email(self, email):
                self.email = email

            def get_discount(self):
                return self.discount

            def set_Discount(self, discount):
                self.discount = discount
        # <> fin Cliente


        class InvoiceSales(ProductDetalle, Cliente):
            def __init__(self):
                super(InvoiceSales, self).__init__()
                ProductDetalle.__init__(self)
                Cliente.__init__(self)

                self.user = User()

                self.car = []
                self.classifySales = []
                self.productos = []
                self.cantProd = 0.00
                self.price = 0.00
                self.cantTotal = 0.00
                self.subtotal = 0.00
                self.total = 0.00

                self.mano_obra = 0.00
                self.miscelanea = 0.00
                self.descuento = 0.00
                self.deuda = 0.00

            def set_User(self, user):
                self.user = user

            def addToCar(self):
                exist = False
                for i in set(self.productos):
                    if i == self.get_codCom():
                        exist = True
                        break

                if not exist:
                    self.productos.append(self.get_codCom())
                    self.car.append([self.get_category(), self.get_codFab(), self.get_codCom(), self.get_supplier(),
                                     self.cantProd, self.price, self.subtotal, self.disponibilidad])

                    self.classifySales.append([self.get_Id(), self.cantProd, self.price])
                    self.cantProd = 0.00

                    self.update()

                return exist

            def set_cantProd(self, cant):
                self.cantProd = cant

            def set_price(self, price):
                self.price = price
                self.subtotal = round(price * self.cantProd, 2)

            def update(self):
                self.total = 0
                self.cantTotal = 0
                for i in self.car:
                    self.cantTotal += i[4]
                    self.total += i[6]

            def deleteProducto(self, codCom):
                count = 0
                for i in self.car:
                    if codCom in i:
                        del self.car[count]
                    count += 1
                self.update()

            def set_invoice(self, num):
                self.invoice = "SI-{}".format(num)

            def html(self):
                tablaDetalle = ""
                for category, codFab, codCom, supplier, cantProd, price, subtotal, disponible in self.car:
                    tablaDetalle += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".\
                        format(category, codCom, cantProd, price, subtotal)

                html = """
                <!DOCTYPE html>
        <html class="html" lang="es-ES">
         <head>
          <meta http-equiv="Content-type" content="text/html;charset=UTF-8"/>
          <meta name="keywords" content="hostal, turismo, cuba, habana, havana"/>
          <meta name="generator" content="2015.0.0.309"/>
          <title>Lodging Invoice/ Factura de Alojamiento</title>
          <!-- CSS -->
          <link rel="stylesheet" type="text/css" href="css/site_global.css?4052507572"/>
          <link rel="stylesheet" type="text/css" href="css/index.css?4191106610" id="pagesheet"/>
          <link rel="stylesheet" href="stylesheet.css">
          <script src="config.js"></script>
           </head>
         <body>
          <div class="clearfix" id="page"><!-- column -->
           <div class="clearfix colelem" id="pppu113"><!-- group -->
            <div class="clearfix grpelem" id="ppu113"><!-- column -->
             <div class="clearfix colelem" id="pu113"><!-- group -->
              <div class="rounded-corners clearfix grpelem" id="u113"><!-- column -->
               <div class="position_content" id="u113_position_content">
                <div class="clearfix colelem" id="u115-4"><!-- content -->
                 <p>Concepto/Concept</p>
                </div>
                <div class="clearfix colelem" id="u116-6"><!-- content -->
                 <p>Factura de Venta</p>
                 <p id="u116-4">Sales Invoice</p>
                </div>
               </div>
              </div>
              <div class="rounded-corners grpelem" id="u285"><!-- simple frame --></div>
             </div>
             <div class="clearfix colelem" id="pu118"><!-- group -->
              <div class="rounded-corners clearfix grpelem" id="u118"><!-- column -->
               <div class="position_content" id="u118_position_content">
                <div class="clearfix colelem" id="u119-4"><!-- content -->
                 <p>Factura/Invoice</p>
                </div>
                <div class="clearfix colelem" id="u120-4"><!-- content -->
                 <p>{invoice}</p>
                </div>
               </div>
              </div>
              <div class="rounded-corners grpelem" id="u286"><!-- simple frame --></div>
             </div>
             <div class="clearfix colelem" id="pu121"><!-- group -->
              <div class="rounded-corners clearfix grpelem" id="u121"><!-- column -->
               <div class="position_content" id="u121_position_content">
                <div class="clearfix colelem" id="u122-4"><!-- content -->
                 <p>Fecha/Date</p>
                </div>
                <div class="clearfix colelem" id="u123-4"><!-- content -->
                 <p>2017-08-25</p>
                </div>
               </div>
              </div>
              <div class="rounded-corners grpelem" id="u287"><!-- simple frame --></div>
             </div>
             <div class="clearfix colelem" id="pu124"><!-- group -->
              <div class="rounded-corners clearfix grpelem" id="u124"><!-- column -->
               <div class="position_content" id="u124_position_content">
                <div class="clearfix colelem" id="u125-4"><!-- content -->
                 <p>Usuario/User</p>
                </div>
                <div class="clearfix colelem" id="u126-4"><!-- content -->
                 <p>{user}</p>
                </div>
               </div>
              </div>
              <div class="rounded-corners grpelem" id="u288"><!-- simple frame --></div>
             </div>
            </div>
            <div class="clip_frame grpelem" id="u75"><!-- image -->
             <img class="block" id="u75_img" src="images/ledea auto air.png" alt="" width="166" height="75"/>
            </div>
            <div class="clearfix grpelem" id="pu81-16"><!-- column -->
                 <div class="clearfix colelem" id="u81-16"><!-- content -->
                  <p id="u81-2"><span id="u81">Dirección</span></p>
                  <p>Calle Reina 55 entre Ángeles y Águila, Planta Alta</p>
                  <p>Centro Habana, La Habana, Cuba</p>
                  <p id="u81-8"><span id="u81-7">Teléfono</span></p>
                  <p>&nbsp;+53 53342668</p>
                  <p>&nbsp;+53 52958250</p>
                  <p id="u81-12"><span id="u81-11">Email</span></p>
                  <p>mueblesatlantis.habana@gmail.com</p>
                  <p>www.facebook.com/muebles atlantis cuba</p>
                 </div>
                 <div class="clearfix colelem" id="pu313-10"><!-- group -->
                  <div class="clearfix grpelem" id="u313-10"><!-- content -->
                   <p id="u313-2"><span id="u313">Developer</span></p>
                   <p id="u313-4">Josué Isai Hernández Sánchez</p>
                   <p id="u313-6">josueisaihs@gmail.com</p>
                   <p id="u313-8">+53 53861204</p>
                  </div>
                  <div class="clip_frame grpelem" id="u314"><!-- image -->
                   <img class="block" id="u314_img" src="images/logo%20elijosoft%20150.png" alt="" width="100%" style="padding-top: 30%" />
                  </div>
                  <div class="rounded-corners clearfix grpelem" id="u318"><!-- group -->
                   <div class="grpelem" id="u316"><!-- rasterized frame --></div>
                  </div>
                 </div>
                 <div class="clearfix colelem" id="pu313-10"><!-- group -->
                  <div class="clearfix grpelem" id="u313-10"><!-- content -->
                   <p id="u313-4">6ta Nº204 entre Fomento y Albear, Cerro, La Habana</p>
                   <p id="u313-6">ventas@softwaresinlimite.com</p>
                   <p id="u313-8">+53 56142378</p>
                  </div>
                  <div class="clip_frame grpelem" id="u314"><!-- image -->
                   <img class="block" id="u314_img" src="images/dossl.png" alt="" width="100%" style="padding-top: 30%" />
                  </div>
                  <div class="rounded-corners clearfix grpelem" id="u318"><!-- group -->
                   <div class="grpelem" id="u316"><!-- rasterized frame --></div>
                  </div>
                 </div> 
                </div>
               </div>
           <div class="colelem" id="u277"><!-- simple frame --></div>
           <div class="clearfix colelem" id="u280-4"><!-- content -->
            <p>Productos/Products</p>
           </div>
           <div class="colelem" id="u273"><!-- custom html -->
                <table>
                    <tr class="inicio">
                        <td>Cliente</td><td>Telef</td><td>Condicion</td><td>Descuento</td><td>Deuda</td>
                        <td>Mano Obra</td><td>Miscelanea</td><td>Total</td>
                    </tr>
                    <tr>
                        <td>{cliente}</td><td>{telef}</td><td>Efectivo</td><td>{descuento}</td><td>{deuda}</td>
                        <td>{mano_obra}</td><td>{miscelanea}</td><td class="total">{total}</td>
                    </tr>
                </table>
                </div>
                   <div class="colelem" id="u275"><!-- custom html -->
                <table>
                    <tr class="inicio">
                        <td>Categoria</td><td>Codigo</td><td>Cantidad</td><td>Precio</td><td>Subtotal</td>
                    </tr>
                    {tablaDetalle}
                </table>
                </div>
                   <div class="clearfix colelem" id="pu278-7"><!-- group -->
                    <div class="clearfix grpelem" id="u278-7"><!-- content -->
                     <p id="u278-2">______________________</p>
                     <p id="u278-4">Firma Cliente</p>
                     <p>&nbsp;</p>
                    </div>
                    <div class="clearfix grpelem" id="u279-7"><!-- content -->
                     <p id="u279-2">______________________</p>
                     <p id="u279-4">Firma Usuario</p>
                     <p>&nbsp;</p>
                    </div>
                   </div>
                   <div class="clearfix colelem" id="pu325"><!-- group -->
                    <div class="clearfix grpelem" id="u325"><!-- column -->
                     <div class="position_content" id="u325_position_content">
                      <div class="clearfix colelem" id="u329-4"><!-- content -->
                       <p>Recibo de Venta/Sales Voucher</p>
                      </div>
                      <div class="clearfix colelem" id="pu326-7"><!-- group -->
                       <div class="clearfix grpelem" id="u326-7"><!-- content -->
                        <p id="u326-2">______________________</p>
                        <p id="u326-4">Firma Cliente</p>
                        <p>&nbsp;</p>
                       </div>
                       <div class="clearfix grpelem" id="u327-7"><!-- content -->
                        <p id="u327-2">______________________</p>
                        <p id="u327-4">Firma Usuario</p>
                        <p>&nbsp;</p>
                       </div>
                      </div>
                     </div>
                    </div>
                    <div class="clearfix grpelem" id="u328-4"><!-- content -->
                     <p>Invoice: {invoice}</p>
                    </div>
                   </div>
                   <div class="verticalspacer"></div>
                  </div>
                   </body>
                </html>""".format(
                    invoice=self.invoice,
                    pubdate=datetime.date.today(),
                    user=self.user,
                    cliente=self.get_name(),
                    telef=self.get_phone(),
                    descuento=self.descuento,
                    mano_obra=self.mano_obra,
                    miscelanea=self.miscelanea,
                    deuda=self.deuda,
                    total=self.total,
                    tablaDetalle=tablaDetalle,
                )

                with open(os.path.join("system", "templete", "index.html"), "w", encoding="UTF-8") as file:
                    file.write(html)
                    file.close()
                os.startfile(os.path.join("system", "templete", "index.html"))

            def set_descuento(self, descuento):
                self.descuento = descuento
        # <> fin InvoiceSales


        class KardexDetalle(ProductDetalle):
            def __init__(self):
                ProductDetalle.__init__(self)
                self.concepto = "Compra"
                self.fecha = 0
                self.kardex = 0
                self.kardexCosto = 0
                self.kardexCotizacion = 0

            def getSQL(self):
                return self.fecha, self.category, self.codFab, self.codCom, self.kardex, self.costProd, self.kardexCosto, self.kardexCotizacion

            def getDetalle(self):
                return self.fecha, 'Compra', self.kardex
        # <> fin KardexDetalle


        class Kardex:
            def __init__(self):
                self.kardexTotal = 0
                self.kardexCostoTotal = 0
                self.kardexCotizacionTotal = 0
                self.kardexList = list()
                self.kardexDetalle = list()

                self.kardexDetalleClass = KardexDetalle()

            def addKardex(self, kardex):
                self.kardexTotal += kardex.kardex
                self.kardexCostoTotal += kardex.kardexCosto
                self.kardexCotizacionTotal += kardex.kardexCotizacion
                self.kardexList.append(kardex.getSQL())
                self.kardexDetalle.append(kardex.getDetalle())

                self.kardexDetalleClass = kardex
        # <> fin Kardex


        class InvoiceKardex(KardexDetalle):
            def __init__(self):
                super(InvoiceKardex, self).__init__()
                KardexDetalle.__init__(self)

                self.user = ""
                self.invoice = ""
                self.id_invoice = 0

            def set_User(self, user):
                self.user = user

            def set_invoice(self, num):
                self.invoice = "KI-{}".format(num)

            def getKardexDetalleSQL(self):
                return self.id_invoice, self.get_Id(), self.kardex

            def getKardexSQL(self):
                return self.id_invoice, 0, round(self.kardex * self.costProd, 2)

            def getKardexFinanzas(self):
                return self.fecha, self.invoice, 'Compra', 0.00, self.kardexCosto, self.get_detailKardex()

            def get_detailKardex(self):
                if self.kardex > 1:
                    plural = "es"
                else:
                    plural = ""
                return "Compra de {kardex} unidad{plu} de {component} {codeFab} ({codeCom})".\
                    format(kardex=self.kardex, component=self.get_category(), codeFab=self.get_codFab(),
                           codeCom=self.get_codCom(), plu=plural)
        # <> fin InvoiceKardex


        class SalesDetalle(InvoiceSales):
            def __init__(self):
                InvoiceSales.__init__(self)
                self.concepto = "Venta"
                self.fecha = 0
                self.ventaCosto = 0
                self.ventaUtilidad = 0
        # <> fin SalesDetalle


        class Finanzas:
            def __init__(self):
                self.debe = 0
                self.haber = 0
                self.total = 0

                self.conceptoVentasTag = "Venta"
                self.conceptoKardexTag = "Kardex"
                self.conceptoDescuentoTag = "Descuento"
                self.conceptoDeudaTag = "Deuda"

                self.conceptoVentas = 0
                self.conceptoKardex = 0
                self.conceptoDescuento = 0
                self.conceptoDeuda = 0

                self.totalList = list()
                self.conceptoKardexList = []
                self.conceptoVentasList = []
                self.conceptoDescuentoList = []
                self.conceptoDeudaList = []

                self.haber = 0
                self.debe = 0
                self.total = 0

            def updateTotal(self):
                self.total = self.debe + self.haber

            def addConceptoKardex(self, invoiceKardex):
                self.totalList.append(invoiceKardex.getKardexFinanzas())
                self.conceptoKardexList.append(invoiceKardex.getKardexFinanzas())
                self.conceptoKardex -= invoiceKardex.kardexCosto
                self.haber += abs(invoiceKardex.kardexCosto)
                self.updateTotal()

            def addConceptoSales(self, finanzasSales):
                self.totalList.append(finanzasSales.getSalesFinanzas())
                self.conceptoVentasList.append(finanzasSales.getSalesFinanzas())
                self.conceptoVentas += (finanzasSales.debe + abs(finanzasSales.haber))
                self.haber += abs(finanzasSales.haber)
                self.debe += finanzasSales.debe
                self.updateTotal()

            def addConceptoDiscount(self, finanzasDiscount):
                self.totalList.append(finanzasDiscount.getDiscountFinanzas())
                self.conceptoDescuentoList.append(finanzasDiscount.getDiscountFinanzas())
                self.conceptoDescuento -= finanzasDiscount.discount
                self.haber += abs(finanzasDiscount.discount)
                self.updateTotal()

            def addConceptoDebt(self, finanzasDebt):
                self.totalList.append(finanzasDebt.getDebtFinanzas())
                self.conceptoDeudaList.append(finanzasDebt.getDebtFinanzas())
                self.conceptoDeuda -= finanzasDebt.debt
                self.haber += abs(finanzasDebt.debt)
                self.updateTotal()

            class Sales:
                producto = ProductDetalle()
                fecha = ""
                client = ""
                invoice = ""
                sale = 0
                haber = 0
                debe = 0

                def getSalesFinanzas(self):
                    return self.fecha, self.invoice, "Venta", self.debe, self.haber, self.getDetail()

                def getDetail(self):
                    if self.sale > 1:
                        plural = "es"
                    else:
                        plural = ""

                    return "Venta a {client} de {sales} unidad{plu} de {component} {codeFab} ({codeCom})".\
                        format(sales=self.sale, plu=plural, component=self.producto.get_category(),
                               codeFab=self.producto.get_codFab(), codeCom=self.producto.get_codCom(), client=self.client)

            class Discount:
                client = ""
                invoice = ""
                fecha = ""
                discount = 0
                porciento = ""

                def getDiscountFinanzas(self):
                    return self.fecha, self.invoice, "Descuento", 0.00, self.discount, self.getDetail()

                def getDetail(self):
                    return "Descuento del {}% a {}".format(self.porciento, self.client)

            class Debt:
                client = ""
                invoice = ""
                fecha = ""
                debt = 0
                pagado = ""

                def getDebtFinanzas(self):
                    return self.fecha, self.invoice, "Deuda", 0.00, self.debt, self.getDetail()

                def getDetail(self):
                    return "{} ha pagado el {}% de su deuda".format(self.client, self.pagado)
        # <> fin Finanzas


        class DebtDetalle:
            def __init__(self):
                super(DebtDetalle, self).__init__()
                self.client = ""
                self.invoice = ""
                self.money = 0
                self.dep = 0
                self.date = ""

            def getDebt(self):
                return self.invoice, self.client, self.date, self.dep, self.money

            def updateMoney(self, val):
                self.money += val
        # <> fin DebtDetalle


        class User:
            id = 0
            user = ""
            pwd = ""
            name = ""
            lastname = ""
            brithday = ""
            sex = ""
            size = ""
            status = ""

            def __sql__(self):
                pin = self.name[0] + self.lastname[0]
                pin = pin.upper()
                return str(base64.b64encode(base64.b64encode(bytes(self.user, 'UTF-8'))))[2:-1], \
                       str(base64.b64encode(base64.b64encode(bytes(self.pwd, 'UTF-8'))))[2:-1], pin, self.status, \
                       self.name, self.lastname

            def isAdmin(self):
                return self.status == "Administrador"
        # <> fin User

        class Inventario(SQL):
            def __init__(self):
                super(Inventario, self).__init__()
                SQL.__init__(self)

                header = ["Ubicación", "Categoría", "Proveedor", "Código", "Modelo", "Cant Alm", "Costo", "Inversion"]
                lista = self.classifyQuery(SELECT="Classify.location, Components.component, Classify.supplier, "
                                                  "Classify.codeCom, Classify.codeFab, Classify.cantAlm, Classify.costProd,"
                                                  "round(Classify.cantAlm * Classify.costProd, 2)",
                                           QUERY=" AND Classify.cantAlm > 0")
                dialogList = DialogList(header, lista, opcion="Inventario")
                dialogList.setWindowTitle("Inventario")
                if len(lista) > 0:
                    dialogList.exec_()
        # <> fin Inventario

        class Worker:
            id = 0
            name = ""
            lastname = ""
            ci = ""
            street = ""
            city = ""
            state = ""
            phone = ""
            phoneOther = ""
            mobil = ""
            mobilOther = ""
            email = ""

            def getSQL(self):
                return self.name, self.lastname, self.ci, self.street, self.city, self.state, self.phone, \
                       self.phoneOther, self.mobil, self.mobilOther, self.email
        # <> fin Worker

        class ElijoSoftSecureLayout(QDialog, dialogLicUi):
            def __init__(self):
                super(ElijoSoftSecureLayout, self).__init__()
                QDialog.__init__(self)
                self.setupUi(self)
                self.setWindowIcon(QIcon(os.path.join("system", "image", "iconocaprisa.png")))

                self.masterSecureAgent = ElijoSoftSecure()

                self.pushButtonRequestLic.clicked.connect(self.genRequest)
                self.pushButtonValLic.clicked.connect(self.setLic)

            def genRequest(self):
                request = self.masterSecureAgent.genRequest(format=True, forLic=True)
                QMessageBox.information(self, "Aviso", "El codigo generado tiene 72 horas de vigencia "
                                                       "para activar la licencia")
                self.lineEdit.setText(request)

            def setLic(self):
                lic = self.lineEdit_2.text()

                licenciaval = re.compile(
                    r"[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}")
                licenciaval = licenciaval.findall(lic)

                if licenciaval != []:
                    is_valid, i = self.masterSecureAgent.registreLic(licenceRef=licenciaval[0])
                    if is_valid:
                        is_valid, i = self.masterSecureAgent.validLic()
                        if is_valid:
                            p = ""
                            if i > 1:
                                p = "s"
                            QMessageBox.information(self, "Aviso", "Licencia activa por {} dia{}"
                                                                   "\nEl programa se cerrara para guardar los cambios".
                                                    format(i, p))
                            self.close()
                        else:
                            QMessageBox.warning(self, "Aviso", "El codigo de licencia esta corrupto")
                    else:
                        QMessageBox.warning(self, "Aviso", "El codigo de licencia esta corrupto")

            def closeEvent(self, event):
                reply = QMessageBox.question(self, 'Confirmación Salida',
                                             "Estás seguro que desea salir", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
        # <> fin ElijoSoftSecureLayout


        class ProductLayout(QDialog, productUi, SQL):
            def __init__(self):
                super(ProductLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.user = User()

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.loadCategoria()
                self.loadProveedor()
                self.connect()

                self.cantCaract = 7

                self.crearPushButton.hide()

            def connect(self):
                self.categoriaComboBox.activated.connect(self.categoriaChanged)
                self.codigoLineEdit.textChanged.connect(self.codigoLineEditChanged)
                self.proveedorAddPushButton.clicked.connect(self.proveedorAdd)
                self.categoriaAddPushButton.clicked.connect(self.categoriaAdd)
                self.crearPushButton.clicked.connect(self.crear)
                self.imagenAddPushButton.clicked.connect(self.imagenAdd)
                self.formatoPushButton.clicked.connect(self.formato)
                self.categoriasPushButton.clicked.connect(self.categoriaEdit)
                self.proveedoresPushButton.clicked.connect(self.proveedorEdit)

            def loadCategoria(self):
                self.categoriaComboBox.clear()
                for i in self.componetsQuery(QUERY=""):
                    self.categoriaComboBox.addItems(i)

            def loadProveedor(self):
                self.proveedorComboBox.clear()
                for i in self.factoryQuery():
                    self.proveedorComboBox.addItems(i)

            def codigoLineEditChanged(self, text):
                if text.__len__() == self.cantCaract:
                    if self.classifyQuery(SELECT="Classify.codeFab", QUERY=" AND Classify.codeFab == '{}'".
                            format(text)).__len__() > 0:
                        QMessageBox.critical(self, "Error", "Este producto ya existe !!")
                        self.crearPushButton.hide()
                    else:
                        self.crearPushButton.show()
                else:
                    self.crearPushButton.hide()

            def proveedorAdd(self):
                dialog = QInputDialog()
                dialog.setWindowTitle("Agregar")
                dialog.setLabelText("Insertar Nuevo Proveedor")
                dialog.setStyleSheet(style)
                if dialog.exec_():
                    if len(self.factoryQuery(QUERY=" AND lower(supplier) == lower('{}')".format(dialog.textValue()))) == 0:
                        QMessageBox.information(self, "Atención",
                                                "<font color='green'>Nuevo Proveedor agregado correctamente !</font>")
                        # self.loadProveedor()
                        self.proveedorComboBox.addItems(("{}".format(dialog.textValue()),))
                    else:
                        QMessageBox.critical(self, "Error",
                                                "<font color='red'>Este Proveedor ya existe !</font>")

            def categoriaAdd(self):
                dialog = QInputDialog()
                dialog.setWindowTitle("Agregar")
                dialog.setLabelText("Insertar Nueva Categoria")
                dialog.setStyleSheet(style)
                if dialog.exec_():
                    if self.componentInsert(dialog.textValue()):
                        QMessageBox.information(self, "Atención",
                                                "<font color='green'>Nueva Categoría agregado correctamente !</font>")
                        self.loadCategoria()
                    else:
                        QMessageBox.critical(self, "Error",
                                             "<font color='red'>Esta Categoría ya existe !</font>")

            def categoriaEdit(self):
                header = ("Categoría",)
                lista = self.componetsQuery()
                dialogList = DialogList(header, lista, opcion="Categoria")
                dialogList.setWindowTitle("Editar Categorías")
                if len(lista) > 0:
                    dialogList.exec_()

            def proveedorEdit(self):
                header = ("Proveedor",)
                lista = self.classifyQuery(SELECT="DISTINCT Classify.supplier")
                dialogList = DialogList(header, lista, opcion="Proveedor")
                dialogList.setWindowTitle("Editar Proveedores")
                if len(lista) > 0:
                    dialogList.exec_()

            def categoriaChanged(self, i):
                self.categoriaComboBox.itemText(i)
                id = self.classifyQuery(SELECT="Classify.codeFab", QUERY=" AND Components.component == '{}'".format(
                    self.categoriaComboBox.itemText(i)))
                if id.__len__() > 0:
                    id = id[0][0][:2]
                    self.codigoLineEdit.setText(id)
                    self.modeloLineEdit.setText("{}-{}".format(
                        id, int(self.sequenceQuery(SELECT="seq", QUERY=" AND name == 'Classify'")[0]) + 1001))
                else:
                    split = self.categoriaComboBox.itemText(i).split(" ")
                    if len(split) > 1:
                        id = split[0][0] + split[1][0]
                    else:
                        id = split[0][:2]
                    id = id.upper()

                    self.codigoLineEdit.setText(id)
                    self.modeloLineEdit.setText("{}-{}".format(
                        id, int(self.sequenceQuery(SELECT="seq", QUERY=" AND name == 'Classify'")[0]) + 1001))

            def imagenAdd(self):
                file = QFileDialog.getOpenFileName(self, "Seleccione Imagen", "", "Imagen (*.png *.jpg)")[0]
                self.imagenLabel_2.setStyleSheet("image: url('{}')".format(file))
                self.imagenLabel_2.setText("{}".format(file))

            def crear(self):
                newProduct = ProductDetalle()
                newProduct.set_category(self.categoriaComboBox.currentText())
                newProduct.set_codFab(self.codigoLineEdit.text())
                newProduct.set_codCom(self.modeloLineEdit.text())
                newProduct.set_costProd(self.costoDoubleSpinBox.value())
                newProduct.set_price1(self.p1DoubleSpinBox.value())
                newProduct.set_price2(self.p2DoubleSpinBox.value())
                newProduct.set_price3(self.p3DoubleSpinBox.value())
                newProduct.set_price4(self.p4DoubleSpinBox.value())
                newProduct.set_cantAlm(self.cantAlmacenDoubleSpinBox.value())
                newProduct.set_supplier(self.proveedorComboBox.currentText())
                newProduct.set_flete(self.fleteDoubleSpinBox.value())
                newProduct.set_location(self.ubicacionLineEdit.text())
                newProduct.set_cantMin(self.cantMinimaDoubleSpinBox.value())
                newProduct.set_tax(self.impuestoDoubleSpinBox.value())
                newProduct.set_detail(self.descripcionTextEdit.toPlainText())

                if self.imagenLabel_2.text() != "":
                    nom = self.codigoLineEdit.text().replace("-", "")
                    nom = nom.lower()
                    cf(self.imagenLabel_2.text(), os.path.join("system", "media", "300px", "{}.{}".
                                                               format(
                        nom, imghdr.what(self.imagenLabel_2.text()))))

                if self.classifyInsert([newProduct]):
                    QMessageBox.information(self, "Aviso", "Nuevo producto creado satisfactoriamente !")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Nuevo producto no ha sido creado :(")

            def formato(self):
                dialog = QInputDialog()
                dialog.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                dialog.setWindowTitle("Nuevo Código")
                dialog.setLabelText("Escriba el código del producto:")
                dialog.setStyleSheet(style)
                formato = ""
                formato.isalpha()
                if dialog.exec_():
                    codigo = dialog.textValue().upper()

                    for i in codigo:
                        if i.isalpha():
                            formato += ">A"
                        elif i.isnumeric():
                            formato += "9"
                        else:
                            formato += i
                    self.cantCaract = codigo.__len__()
                    self.codigoLineEdit.setInputMask(formato)
                    self.codigoLineEdit.setText(codigo)
        # <> fin ProductLayout


        class SearcherLayout(QDialog, searcherUi, SQL):
            def __init__(self, permission=("Detalle", "Compra")):
                super(SearcherLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.user = User()

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.m_iconSize = QSize(100, 100)
                self.listWidgetPicker.setIconSize(self.m_iconSize)
                self.listWidgetPicker.setMinimumHeight(self.m_iconSize.height() + 50)

                self.labelImagen.setStyleSheet("image: url(system/image/elijosoft_searcher.png)")

                self.permission = permission

                self.connection()

                self.producto = None

                self.listWidgetPicker.clear()
                for i in self.classifyQuery(SELECT="Classify.codeFab, Classify.codeCom, Classify.detail",
                                            QUERY=" AND Classify.codeCom GLOB '*' LIMIT 250"):
                    self.loadListWidgetPicker(i)

            def connection(self):
                self.listWidgetPicker.itemDoubleClicked.connect(self.listWidgetPickerDoubleClicked)
                self.searchLineEdit.textChanged.connect(self.search)

            def loadListWidgetPicker(self, i):
                img = i[0].lower()
                img = img.replace("-", "")
                item = QListWidgetItem()
                if os.path.exists(os.path.join("system", "media", "300px", "{}.jpg".format(img))):
                    item.setIcon(QIcon(os.path.join("system", "media", "300px", "{}.jpg".format(img))))
                elif os.path.exists(os.path.join("system", "media", "300px", "{}.png".format(img))):
                    item.setIcon(QIcon(os.path.join("system", "media", "300px", "{}.png".format(img))))
                else:
                    item.setIcon(QIcon(os.path.join("system", "media", "300px", "vacio.jpg")))
                text = "Code: {codigo}\nModel: {modelo}\n\n{detalle}...". \
                    format(codigo=i[0], modelo=i[1], detalle=i[2][:30])
                item.setText(text)
                self.listWidgetPicker.addItem(item)

            def listWidgetPickerDoubleClicked(self, item):
                dialog = DialogOpcionLayout(self.permission)
                texto = item.text()
                code, model, _, __ = texto.split("\n")
                code = code.replace("Code: ", "")
                model = model.replace("Model: ", "")
                self.producto = ProductDetalle()
                self.producto.set_codFab(code)
                self.producto.set_codCom(model)

                if dialog.exec_():
                    if dialog.action == dialog.actionAdd:
                        self.updateProducto()
                        self.accept()
                    elif dialog.action == dialog.actionDetalle:
                        self.updateProducto()
                        detalle = DialogSelectLayout(self.producto)
                        detalle.exec_()
                    elif dialog.action == dialog.actionKardex:
                        self.updateProducto()
                        dialogKardex = QInputDialog()
                        dialogKardex.setWindowTitle("Compra")
                        dialogKardex.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                        dialogKardex.setLabelText("Code: {}\nModel: {}\nCant Alm: {}\n\nInsertar la cantidad agregada".
                                                  format(self.producto.get_codFab(), self.producto.get_codCom(),
                                                         self.producto.get_cantAlm()))
                        dialogKardex.setInputMode(QInputDialog.DoubleInput)
                        dialogKardex.setDoubleMaximum(1000)
                        dialogKardex.setStyleSheet(style)
                        if dialogKardex.exec_():
                            if dialogKardex.doubleValue() > 0:
                                try:
                                    invoiceKardex = InvoiceKardex()
                                    print(self.user.user)
                                    invoiceKardex.set_User(self.user.user)
                                    invoiceKardex.set_invoice(self.sequenceQuery("seq", "AND name == 'Invoices'")[0] + 1)
                                    invoiceKardex.kardex = float(dialogKardex.doubleValue())
                                    invoiceKardex.set_Id(self.producto.get_Id())
                                    invoiceKardex.set_costProd(self.producto.get_costProd())

                                    self.invoiceKardexInsert(invoiceKardex)

                                    self.producto.add_cantAlm(dialogKardex.doubleValue())
                                    self.classifyUpdate([self.producto])
                                    QMessageBox.information(self, "Información", "Compra realizado correctamente :)")
                                except:
                                    QMessageBox.critical(self, "Error", "Compra no ejecutado\nReinicie el programa e "
                                                                        "intente la operación nuevamente :(")
                            else:
                                QMessageBox.warning(self, "Atención", "No se agregó ningún producto :(")

            def search(self, tx):
                MAKE = re.compile(r"\w{2,30}")
                MAKE = MAKE.findall(tx)

                CODCOM = re.compile(r"([a-z]{1,2})(-\d{1,5}|-)", re.I)
                CODCOM = CODCOM.findall(tx)

                CODFAB = re.compile(r"([a-z]{1,2})(-\d{1,5}[a-z]{0,4}|-\d{1,4}|-)", re.I)
                CODFAB = CODFAB.findall(tx)

                _QUERY_CODCOM_ = ""
                if CODCOM.__len__() > 1:
                    for i in CODCOM:
                        _QUERY_CODCOM_ = _QUERY_CODCOM_.__add__(
                            "C.codeCom GLOB '*{}*' OR ".format("{}{}".format(i[0].upper(), i[1])))
                elif CODCOM.__len__() == 1:
                    _QUERY_CODCOM_ = _QUERY_CODCOM_.__add__("C.codeCom GLOB '*{}*' OR ".format("{}{}".
                                                                                               format(CODCOM[0][0].upper(),
                                                                                                      CODCOM[0][1])))
                _QUERY_CODCOM_ = _QUERY_CODCOM_[:-4]

                _QUERY_CODFAB_ = ""
                if CODFAB.__len__() > 1:
                    for i in CODFAB:
                        _QUERY_CODFAB_ = _QUERY_CODFAB_.__add__(
                            "C.codeFab GLOB '*{}*' OR ".format("{}{}".format(i[0].upper(), i[1])))
                elif CODFAB.__len__() == 1:
                    _QUERY_CODFAB_ = _QUERY_CODFAB_.__add__("C.codeFab GLOB '*{}*' OR ".format("{}{}".
                                                                                               format(CODFAB[0][0].upper(),
                                                                                                      CODFAB[0][1])))
                _QUERY_CODFAB_ = _QUERY_CODFAB_[:-4]

                _QUERY_CLASSIFY_ = ""
                if _QUERY_CODCOM_ != "":
                    _QUERY_CLASSIFY_ = _QUERY_CLASSIFY_.__add__(_QUERY_CODCOM_)

                if _QUERY_CODFAB_ != "":
                    _QUERY_CLASSIFY_ = _QUERY_CLASSIFY_.__add__(" OR {}".format(_QUERY_CODFAB_))

                _QUERY_MAKE_ = ""
                if MAKE.__len__() > 1:
                    for i in MAKE:
                        _QUERY_MAKE_ = _QUERY_MAKE_.__add__("(Ma.make GLOB '{make}*' OR Mo.model GLOB '{make}*') OR ".
                                                            format(make=i.upper()))
                elif MAKE.__len__() == 1:
                    _QUERY_MAKE_ = _QUERY_MAKE_.__add__("(Ma.make GLOB '{make}*' OR Mo.model GLOB '{make}*') OR ".
                                                        format(make=MAKE[0].upper()))
                _QUERY_MAKE_ = _QUERY_MAKE_[:-4]

                SELECT = "C.codeFab, C.codeCom, C.detail"

                QUERY_CLASSIFY = ""
                if _QUERY_CLASSIFY_ != "":
                    QUERY_CLASSIFY += " AND ({})".format(_QUERY_CLASSIFY_)

                QUERY_MAKE = ""
                if _QUERY_MAKE_ != "":
                    QUERY_MAKE += " AND ({})".format(_QUERY_MAKE_)

                self.listWidgetPicker.clear()
                if QUERY_CLASSIFY != "" or QUERY_MAKE != "":
                    for i in self.spinerSearchQuery(SELECT, QUERY_CLASSIFY, QUERY_MAKE):
                        self.loadListWidgetPicker(i)
                else:
                    for i in self.classifyQuery(SELECT="Classify.codeFab, Classify.codeCom, Classify.detail",
                                                QUERY=" AND Classify.codeCom GLOB '*' LIMIT 250"):
                        self.loadListWidgetPicker(i)

            def updateProducto(self):
                detalles = self.classifyQuery(
                    SELECT="Components.component, Classify.costProd, Classify.price1, Classify.price2, "
                           "Classify.price3, Classify.price4, Classify.cantAlm, Classify.supplier, "
                           "Classify.flete, Classify.location, Classify.cantMin, Classify.tax, "
                           "Classify.detail, Classify.fullbarcode, Classify.id",
                    QUERY=" AND Classify.codeCom == '{}' AND Classify.codeFab == '{}'".format(
                        self.producto.get_codCom(), self.producto.get_codFab()))[0]
                self.producto.set_category(detalles[0])
                self.producto.set_costProd(detalles[1])
                self.producto.set_price1(detalles[2])
                self.producto.set_price2(detalles[3])
                self.producto.set_price3(detalles[4])
                self.producto.set_price4(detalles[5])
                self.producto.set_cantAlm(detalles[6])
                self.producto.set_supplier(detalles[7])
                self.producto.set_flete(detalles[8])
                self.producto.set_location(detalles[9])
                self.producto.set_cantMin(detalles[10])
                self.producto.set_tax(detalles[11])
                self.producto.set_detail(detalles[12])
                self.producto.set_barcode(detalles[13])
                self.producto.set_Id(detalles[14])
        # <> fin SearcherLayout


        class DialogOpcionLayout(QDialog, dialogOpcionUi):
            def __init__(self, permission=("Add", "Detalle", "Compra")):
                super(DialogOpcionLayout, self).__init__()
                self.setupUi(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.action = None
                self.actionAdd = "Add"
                self.actionDetalle = "Detalle"
                self.actionKardex = "Compra"
                self.actionEditar = "Editar"
                self.actionEliminar = "Eliminar"

                self.addPushButton.hide()
                self.verDetallePushButton.hide()
                self.kardexPushButton.hide()
                self.editarPushButton.hide()
                self.eliminarPushButton.hide()

                for i in permission:
                    if i == self.actionAdd:
                        self.addPushButton.show()

                    if i == self.actionDetalle:
                        self.verDetallePushButton.show()

                    if i == self.actionKardex:
                        self.kardexPushButton.show()

                    if i == self.actionEditar:
                        self.editarPushButton.show()

                    if i == self.actionEliminar:
                        self.eliminarPushButton.show()

                self.conection()

            def conection(self):
                self.verDetallePushButton.clicked.connect(self.verDetalle)
                self.addPushButton.clicked.connect(self.add)
                self.kardexPushButton.clicked.connect(self.kardex)
                self.editarPushButton.clicked.connect(self.editar)
                self.eliminarPushButton.clicked.connect(self.eliminar)

            def add(self):
                self.action = self.actionAdd
                self.accept()

            def verDetalle(self):
                self.action = self.actionDetalle
                self.accept()

            def kardex(self):
                self.action = self.actionKardex
                self.accept()

            def editar(self):
                self.action = self.actionEditar
                self.accept()

            def eliminar(self):
                self.action = self.actionEliminar
                self.accept()
        # <> fin DialogOpcionLayout


        class DialogSelectLayout(QDialog, dialogSelectUi, SQL):
            def __init__(self, producto):
                super(DialogSelectLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.producto = producto

                self.loadWidgets()

                self.deletePushButton.hide()
                self.okPushButton.hide()
                self.cancelPushButton.hide()

                self.conection()

            def conection(self):
                self.editarPushButton.clicked.connect(self.editar)
                self.okPushButton.clicked.connect(self.editarOk)
                self.cancelPushButton.clicked.connect(self.editarCancel)
                self.makeTreeWidget.itemDoubleClicked.connect(self.nuevaMarca)

            def editar(self):
                self.deletePushButton.hide()
                self.editarPushButton.hide()
                self.okPushButton.show()
                self.cancelPushButton.show()
                self.readOnly(False)

            def editarCancel(self):
                # self.deletePushButton.show()
                self.loadWidgets()
                self.editarPushButton.show()
                self.okPushButton.hide()
                self.cancelPushButton.hide()
                self.readOnly(True)

            def editarOk(self):
                try:
                    # self.deletePushButton.show()
                    self.editarPushButton.show()
                    self.okPushButton.hide()
                    self.cancelPushButton.hide()
                    self.readOnly(True)

                    self.producto.set_costProd(self.costoDoubleSpinBox.value())
                    self.producto.set_price1(self.p1DoubleSpinBox.value())
                    self.producto.set_price2(self.p2DoubleSpinBox.value())
                    self.producto.set_price3(self.p3DoubleSpinBox.value())
                    self.producto.set_price4(self.p4DoubleSpinBox.value())
                    self.producto.set_cantAlm(self.cantAlmacenDoubleSpinBox.value())
                    self.producto.set_flete(self.fleteDoubleSpinBox.value())
                    self.producto.set_location(self.ubicacionLineEdit.text())
                    self.producto.set_cantMin(self.cantMinimaDoubleSpinBox.value())
                    self.producto.set_tax(self.impuestoDoubleSpinBox.value())
                    self.producto.set_detail(self.descripcionTextEdit.toPlainText())

                    self.classifyUpdate([self.producto])

                    QMessageBox.information(self, "Aviso", "Producto editado satisfactoriamente !")
                except:
                    pass

            def readOnly(self, bool):
                # self.categoriaLineEdit.setReadOnly(bool)
                # self.codigoLineEdit.setReadOnly(bool)
                # self.modeloLineEdit.setReadOnly(bool)
                self.costoDoubleSpinBox.setReadOnly(bool)
                self.p1DoubleSpinBox.setReadOnly(bool)
                self.p2DoubleSpinBox.setReadOnly(bool)
                self.p3DoubleSpinBox.setReadOnly(bool)
                self.p4DoubleSpinBox.setReadOnly(bool)
                self.cantAlmacenDoubleSpinBox.setReadOnly(bool)
                # self.proveedorLineEdit.setReadOnly(bool)
                self.fleteDoubleSpinBox.setReadOnly(bool)
                self.ubicacionLineEdit.setReadOnly(bool)
                self.cantMinimaDoubleSpinBox.setReadOnly(bool)
                self.impuestoDoubleSpinBox.setReadOnly(bool)
                self.descripcionTextEdit.setReadOnly(bool)

            def loadWidgets(self):
                self.categoriaLineEdit.setText(self.producto.get_category())
                self.codigoLineEdit.setText(self.producto.get_codFab())
                self.modeloLineEdit.setText(self.producto.get_codCom())
                self.costoDoubleSpinBox.setValue(self.producto.get_costProd())
                self.p1DoubleSpinBox.setValue(self.producto.get_price1())
                self.p2DoubleSpinBox.setValue(self.producto.get_price2())
                self.p3DoubleSpinBox.setValue(self.producto.get_price3())
                self.p4DoubleSpinBox.setValue(self.producto.get_price4())
                self.cantAlmacenDoubleSpinBox.setValue(self.producto.get_cantAlm())
                self.proveedorLineEdit.setText(self.producto.get_supplier())
                self.fleteDoubleSpinBox.setValue(self.producto.get_flete())
                self.ubicacionLineEdit.setText(self.producto.get_location())
                self.cantMinimaDoubleSpinBox.setValue(self.producto.get_cantMin())
                self.impuestoDoubleSpinBox.setValue(self.producto.get_tax())
                self.descripcionTextEdit.setPlainText(self.producto.get_detail())

                img = self.producto.get_codFab().lower()
                img = img.replace("-", "")
                if os.path.exists(os.path.join("system", "media", "300px", "{}.jpg".format(img))):
                    text = r"system/media/300px/{}.jpg".format(img)
                else:
                    text = r"system/media/300px/vacio.jpg"
                self.imagenLabel.setStyleSheet("image: url({})".format(text))

                self.imagenBarcodeLabel.setStyleSheet("image: url(system/media/barcode/{}.png)".format(self.producto.get_barcode()))

                makes = self.makeQuery(QUERY=" AND C.codeCom == '{}'".format(self.producto.get_codCom()))
                self.makeTreeWidget.clear()
                for i in makes:
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.makeTreeWidget.addTopLevelItem(item)
                else:
                    item = QTreeWidgetItem(["Double Click para agregar"])
                    self.makeTreeWidget.addTopLevelItem(item)

                kardex = self.kardexClassifyQuery(QUERY="AND C.codeCom == '{}'".format(self.producto.get_codCom()))
                sales = self.salesClassifyQuery(SELECT="El.time, 'Ventas', Cs.cant", QUERY="AND C.codeCom == '{}'".
                                                format(self.producto.get_codCom()))
                lista = []
                lista.extend(kardex.kardexDetalle)
                lista.extend(sales)
                self.treeWidgetEvents.clear()
                for i in lista:
                    elem = []
                    for k in i:
                        elem.append(str(k))

                    item = QTreeWidgetItem(elem)
                    if elem[1] == "Ventas":
                        icon = QIcon(os.path.join("system", "image", "status_malo.png"))
                    else:
                        icon = QIcon(os.path.join("system", "image", "status_bueno.png"))
                    item.setIcon(1, icon)

                    self.treeWidgetEvents.addTopLevelItem(item)
                self.treeWidgetEvents.sortItems(0, 0)

            def nuevaMarca(self):
                dialogMake = DialogMakeLayout(self.producto.get_codCom())
                if dialogMake.exec_():
                    self.loadWidgets()
        # <> fin DialogSelectLayout


        class DialogMakeLayout(QDialog, dialogMakeUi, SQL):
            def __init__(self, codCom):
                super(DialogMakeLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.loadMakes()

                self.okPushButton.hide()

                self.modelsTreeWidget.setEnabled(False)
                self.modelLineEdit.setEnabled(False)
                self.addModelPushButton.setEnabled(False)

                self.codCom = codCom
                self.make = ""
                self.model = ""
                self.year = 0
                self.engine = ""

                self.connection()

            def connection(self):
                self.makeLineEdit.textChanged.connect(self.searchMake)
                self.makesTreeWidget.itemDoubleClicked.connect(self.makeSelect)
                self.modelsTreeWidget.itemDoubleClicked.connect(self.modelSelect)
                self.modelLineEdit.textChanged.connect(self.searchModel)
                self.addMakePushButton.clicked.connect(self.addMake)
                self.addModelPushButton.clicked.connect(self.addModel)
                self.okPushButton.clicked.connect(self.ok)
                self.cancelPushButton.clicked.connect(self.cancel)

            def loadMakes(self, QUERY="make GLOB '*'"):
                self.makesTreeWidget.clear()
                for i in self.queryFree("make", "Makes", QUERY):
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.makesTreeWidget.addTopLevelItem(item)

            def loadModels(self, QUERY="Makes.make GLOB '{}' AND Models.model GLOB '*' AND Makes.id == Models.id_make"):
                self.modelsTreeWidget.clear()
                for i in self.queryFree("Models.model", "Makes, Models", QUERY):
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.modelsTreeWidget.addTopLevelItem(item)

            def searchMake(self, txt):
                if txt != "":
                    self.loadMakes("make GLOB '*{}*'".format(txt.upper()))
                else:
                    self.loadMakes()

            def makeSelect(self, item):
                self.make = item.text(0)

                self.modelsTreeWidget.setEnabled(True)
                self.modelLineEdit.setEnabled(True)
                self.addModelPushButton.setEnabled(True)

                self.loadModels("Makes.make GLOB '{}' AND Models.model GLOB '*' AND Makes.id == Models.id_make".
                                format(self.make))

            def modelSelect(self, item):
                self.model = item.text(0)

                self.okPushButton.show()

            def searchModel(self, txt):
                if txt != "":
                    self.loadModels("Makes.make GLOB '{}' AND Models.model GLOB '*{}*' AND Makes.id == Models.id_make".
                                    format(self.make, txt.upper()))
                else:
                    self.loadModels("Makes.make GLOB '{}' AND Models.model GLOB '*' AND Makes.id == Models.id_make".
                                   format(self.make))

            def addMake(self):
                dialog = QInputDialog()
                dialog.setWindowTitle("Agregar")
                dialog.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                dialog.setLabelText("Insertar Marca")
                dialog.setStyleSheet(style)
                if dialog.exec_():
                    newMake = dialog.textValue().upper()
                    if self.makeInsert(newMake):
                        self.loadMakes()
                        QMessageBox.information(self, "Aviso", "Marca insertada correctamente !")
                    else:
                        QMessageBox.critical(self, "Error", "Marca ya ha sido insertada :(")

            def addModel(self):
                self.engine = self.motorLineEdit.text()

                dialog = QInputDialog()
                dialog.setWindowTitle("Agregar")
                dialog.setLabelText("Insertar Modelo")
                dialog.setStyleSheet(style)
                if dialog.exec_():
                    newModel = dialog.textValue().upper()
                    if self.modelInsert([self.make, newModel, self.engine]):
                        self.loadModels("Makes.make GLOB '{}' AND Models.model GLOB '*' AND Makes.id == Models.id_make".
                                        format(self.make))
                        QMessageBox.information(self, "Aviso", "Modelo insertado correctamente !")
                    else:
                        QMessageBox.critical(self, "Error", "Modelo ya ha sido insertado :(")

            def cancel(self):
                self.reject()

            def ok(self):
                self.year = self.yearSpinBox.value()
                if self.year < 1950:
                    self.year = 0

                self.engine = self.motorLineEdit.text()

                if self.classifyMakeInsert([self.codCom, self.make, self.model, self.year, self.engine]):
                    QMessageBox.information(self, "Aviso", "Nueva referencia creada correctamente !")
                    self.accept()
                else:
                    pass
        # <> fin DialogMakeLayout


        class SalesLayout(QDialog, salesUi, SQL):
            def __init__(self):
                super(SalesLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.user = User()

                self.producto = ProductDetalle()
                self.cliente = Cliente()
                style_ = """
                QPushButton
        {
         background-color: #F2F2F2;
         font: 10pt;
         color: rgb(67, 136, 101);
         padding: 4px 8px;
         border: 2px solid   rgb(0, 170, 127);
        border-bottom-right-radius: 0px;
        border-bottom-left-radius: 0px;
        border-top-right-radius: 0px;
        border-top-left-radius: 0px;
        image: url(system/image/carrito.png)
         }
        
        :hover
         {
         background-color: #F2F2F2;
         border:  2px solid rgb(120, 200, 29);
         }
        
        :pressed
        {
          border:3px solid rgb(255, 255, 255);
          padding: -1px 1px 1px 1px;
        }"""
                self.carPushButton.setStyleSheet(style_)

                self.invoiceSales = InvoiceSales()

                self.invoiceSales.set_invoice(self.sequenceQuery("seq", "AND name == 'Invoices'")[0] + 1)

                self.addToCarPushButton.hide()
                self.carCantTotalLabel.setText("0.0")

                self.connect()

            def connect(self):
                self.buscarProdPushButton.clicked.connect(self.buscarProd)
                self.carPushButton.clicked.connect(self.car)
                self.addToCarPushButton.clicked.connect(self.addToCar)
                self.cantidadDoubleSpinBox.valueChanged.connect(self.cantAgr)

            def buscarProd(self):
                if self.user.isAdmin():
                    dialog = SearcherLayout(("Detalle", "Add"))
                else:
                    dialog = SearcherLayout(("Add",))

                dialog.user = self.user.user
                if dialog.exec_():
                    self.producto = dialog.producto

                    self.cantidadDoubleSpinBox.setValue(0.0)
                    self.categoriaLineEdit.setText(self.producto.get_category())
                    self.codigoLineEdit.setText(self.producto.get_codFab())
                    self.modeloLineEdit.setText(self.producto.get_codCom())
                    self.cantAlmDoubleSpinBox.setValue(self.producto.get_cantAlm())
                    self.costoDoubleSpinBox.setValue(self.producto.get_costProd())
                    self.radioButton.setText("P1: {}".format(self.producto.get_price1()))
                    self.radioButton_2.setText("P2: {}".format(self.producto.get_price2()))
                    self.radioButton_3.setText("P3: {}".format(self.producto.get_price3()))
                    self.radioButton_4.setText("P4: {}".format(self.producto.get_price4()))

                    self.checkDisponibilidad()

            def car(self):
                self.invoiceSales.set_User(self.user.user)
                dialog = DialogCarLayout(self.invoiceSales, self.user)
                if dialog.exec_():
                    if dialog.action == dialog.action_eliminar:
                        self.invoiceSales.deleteProducto(dialog.item.text(2))
                        self.updateLabel()
                    elif dialog.action == dialog.action_vender:
                        self.invoiceSales = dialog.invoiceSales
                        self.invoiceSalesInsert(self.invoiceSales)

                        for i in self.invoiceSales.car:
                            producto = ProductDetalle()
                            producto.set_codFab(i[1])
                            producto.set_codCom(i[2])
                            producto = self.updateProducto(producto)
                            producto.add_cantAlm(-i[4])
                            self.classifyUpdate([producto,])

                        if self.invoiceSales.deuda > 0:
                            QMessageBox.information(self, "Aviso",
                                                    "Venta realizada de forma <b>exitosa</b> :)\n"
                                                    "pero se guardara la deuda de ${}".format(self.invoiceSales.deuda))
                        else:
                            QMessageBox.information(self, "Aviso",
                                                    "Venta realiada de forma <b>exitosa</b> :)")
                        self.accept()
                    else:
                        pass
                else:
                    pass

            def selectPrice(self):
                count = 0
                for i in [self.radioButton, self.radioButton_2, self.radioButton_3, self.radioButton_4]:
                    count += 1
                    if i.isChecked():
                        break
                prices = {
                    1: self.producto.get_price1(),
                    2: self.producto.get_price2(),
                    3: self.producto.get_price3(),
                    4: self.producto.get_price4(),
                }

                return prices[count]

            def addToCar(self):
                self.invoiceSales.set_Id(self.producto.get_Id())
                self.invoiceSales.set_category(self.producto.get_category())
                self.invoiceSales.set_codFab(self.producto.get_codFab())
                self.invoiceSales.set_codCom(self.producto.get_codCom())
                self.invoiceSales.set_supplier(self.producto.get_supplier())
                self.invoiceSales.set_cantProd(self.cantidadDoubleSpinBox.value())
                self.invoiceSales.set_price(self.selectPrice())
                self.invoiceSales.set_Disponibilidad(self.estadoCheckBox.isChecked())

                if not self.invoiceSales.addToCar():
                    self.categoriaLineEdit.setText("")
                    self.codigoLineEdit.setText("")
                    self.modeloLineEdit.setText("")
                    self.cantAlmDoubleSpinBox.setValue(0.00)
                    self.costoDoubleSpinBox.setValue(0.00)
                    self.cantidadDoubleSpinBox.setValue(0.00)
                    self.radioButton.setText("P1: 0.00")
                    self.radioButton_2.setText("P2: 0.00")
                    self.radioButton_3.setText("P3: 0.00")
                    self.radioButton_4.setText("P4: 0.00")
                    self.producto.set_codCom("")

                self.updateLabel()

            def updateLabel(self):
                self.carCantTotalLabel.setText("{}".format(self.invoiceSales.cantTotal))
                self.CUCDoubleSpinBox.setValue(self.invoiceSales.total)
                self.CUPDoubleSpinBox.setValue(self.invoiceSales.total * 25)

            def cantAgr(self, value):
                if value > 0 and self.producto.get_codCom() != "":
                    self.addToCarPushButton.show()
                    self.labelCantPagar.setText("{}".format(round(value * self.selectPrice(), 2)))
                else:
                    self.addToCarPushButton.hide()
                    self.labelCantPagar.setText("0.00")

                self.checkDisponibilidad()

            def checkDisponibilidad(self):
                if self.producto.get_cantAlm() - self.cantidadDoubleSpinBox.value() > 0:
                    status = Qt.Checked
                else:
                    status = Qt.Unchecked

                self.estadoCheckBox.setCheckState(status)

            def updateProducto(self, producto):
                detalles = self.classifyQuery(
                    SELECT="Components.component, Classify.costProd, Classify.price1, Classify.price2, "
                           "Classify.price3, Classify.price4, Classify.cantAlm, Classify.supplier, "
                           "Classify.flete, Classify.location, Classify.cantMin, Classify.tax, "
                           "Classify.detail, Classify.fullbarcode, Classify.id ",
                    QUERY=" AND Classify.codeCom == '{}' AND Classify.codeFab == '{}' ".
                        format(producto.get_codCom(), producto.get_codFab()))[0]
                producto.set_category(detalles[0])
                producto.set_costProd(detalles[1])
                producto.set_price1(detalles[2])
                producto.set_price2(detalles[3])
                producto.set_price3(detalles[4])
                producto.set_price4(detalles[5])
                producto.set_cantAlm(detalles[6])
                producto.set_supplier(detalles[7])
                producto.set_flete(detalles[8])
                producto.set_location(detalles[9])
                producto.set_cantMin(detalles[10])
                producto.set_tax(detalles[11])
                producto.set_detail(detalles[12])
                producto.set_barcode(detalles[13])
                producto.set_Id(detalles[14])

                return producto
        # <> fin SalesLayout


        class DialogCarLayout(QDialog, dialogCarUi):
            def __init__(self, invoiceSales, user):
                super(DialogCarLayout, self).__init__()
                self.setupUi(self)

                self.user = user

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.invoiceSales = invoiceSales

                self.loadTabla()

                self.totalDoubleSpinBox.setValue(self.invoiceSales.total)

                if self.invoiceSales.total > 0:
                    self.paymentPushButton.show()
                else:
                    self.paymentPushButton.hide()

                self.action = None
                self.action_vender = "Vender"
                self.action_eliminar = "Eliminar"

                self.connection()

            def connection(self):
                self.productoTreeWidget.itemDoubleClicked.connect(self.eliminar)
                self.paymentPushButton.clicked.connect(self.payment)

            def loadTabla(self):
                self.productoTreeWidget.clear()
                for i in self.invoiceSales.car:
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.productoTreeWidget.addTopLevelItem(item)

            def eliminar(self, item):
                reply = QMessageBox.question(self, 'Confirmación',
                                                   "<h2><font color=#FF8822>¿Estás seguro que desea eliminar el {}: {}"
                                                   "?</font></h2>".format(item.text(0), item.text(1)),
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.item = item
                    self.action = self.action_eliminar
                    self.accept()
                else:
                    pass

            def payment(self):
                dialog = DialogPaymentLayout(self.invoiceSales, self.user.user)
                if dialog.exec_():
                    self.invoiceSales = dialog.invoicesSales
                    self.action = self.action_vender
                    self.accept()
        # <> fin DialogCarLayout


        class DialogPaymentLayout(QDialog, dialogPaymentUi):
            def __init__(self, invoiceSales, user):
                super(DialogPaymentLayout, self).__init__()
                self.setupUi(self)

                self.user = user

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.total = 0.0
                self.recibido = 0.0
                self.cambio = 0.0

                self.invoicesSales = invoiceSales

                self.loadTotal(self.invoicesSales.total)

                self.total = self.invoicesSales.total

                self.deudaPushButton.show()
                self.toSellPushButton.hide()

                self.connection()

            def connection(self):
                self.buscarClientePushButton.clicked.connect(self.buscarClient)
                self.miscelaneasDoubleSpinBox.valueChanged.connect(self.changedTotal)
                self.manoObraDoubleSpinBox.valueChanged.connect(self.changedTotal)
                self.descuentoDoubleSpinBox.valueChanged.connect(self.changedTotal)
                self.recibidoCUCDoubleSpinBox.valueChanged.connect(self.changedRecibido)
                self.recibidoCUPDoubleSpinBox.valueChanged.connect(self.changedRecibido)
                self.cambioCUCDoubleSpinBox.valueChanged.connect(self.changedCambioCUC)
                self.cambioCUPDoubleSpinBox.valueChanged.connect(self.changedCambioCUP)
                self.toSellPushButton.clicked.connect(self.toSell)
                self.deudaPushButton.clicked.connect(self.toSellDeuda)

            def loadTotal(self, saldo):
                self.totalCUCDoubleSpinBox.setValue(saldo)
                self.totalCUPDoubleSpinBox.setValue(saldo * 25)

            def buscarClient(self):
                dialog = DialogClientLayout(False)
                dialog.user = self.user
                if dialog.exec_():
                    self.clienteLabel_2.setText(dialog.client[0][0])
                    self.invoicesSales.set_Name(dialog.client[0][0])
                    self.invoicesSales.set_Phone(dialog.client[0][1])
                    self.descuentoDoubleSpinBox.setValue(float(dialog.client[0][2]))

            def changedTotal(self):
                self.total = self.invoicesSales.total + self.miscelaneasDoubleSpinBox.value() +\
                             self.manoObraDoubleSpinBox.value() - self.descuentoDoubleSpinBox.value()

                self.loadTotal(self.total)

                self.invoicesSales.set_descuento(self.descuentoDoubleSpinBox.value())

            def changedRecibido(self):
                self.recibido = self.recibidoCUCDoubleSpinBox.value() + self.recibidoCUPDoubleSpinBox.value() / 25
                self.cambio = self.recibido - self.total

                self.cambioCUCDoubleSpinBox.setMaximum(self.cambio)
                self.cambioCUCDoubleSpinBox.setMinimum(0.0)
                self.cambioCUPDoubleSpinBox.setMaximum(self.cambio * 24)
                self.cambioCUPDoubleSpinBox.setMinimum(0.0)
                self.cambioCUCDoubleSpinBox.setValue(self.cambio)
                self.cambioCUPDoubleSpinBox.setValue(0.0)

                if self.recibido >= self.total:
                    self.toSellPushButton.show()
                    self.deudaPushButton.hide()
                else:
                    self.deudaPushButton.show()
                    self.toSellPushButton.hide()

            def changedCambioCUC(self, value):
                if self.cambio - value > 0:
                    self.cambioCUPDoubleSpinBox.setValue((self.cambio - value) * 24)
                else:
                    self.cambioCUPDoubleSpinBox.setValue(0.00)

            def changedCambioCUP(self, value):
                if self.cambio * 24 - value > 0:
                    self.cambioCUCDoubleSpinBox.setValue((self.cambio * 24 - value) / 24)
                else:
                    self.cambioCUCDoubleSpinBox.setValue(0.00)

            def toSell(self):
                if self.invoicesSales.get_name() != "":
                    self.invoicesSales.mano_obra = self.manoObraDoubleSpinBox.value()
                    self.invoicesSales.miscelanea = self.miscelaneasDoubleSpinBox.value()
                    self.invoicesSales.descuento = self.descuentoDoubleSpinBox.value()
                    self.invoicesSales.html()
                    self.toSellPushButton.hide()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "No ha seleccionado el cliente, si no existe en la base de datos "
                                                        "puede crearlo")

            def toSellDeuda(self):
                if self.invoicesSales.get_name() != "":
                    self.recibido = self.recibidoCUCDoubleSpinBox.value() + self.recibidoCUPDoubleSpinBox.value() / 25
                    self.invoicesSales.mano_obra = self.manoObraDoubleSpinBox.value()
                    self.invoicesSales.miscelanea = self.miscelaneasDoubleSpinBox.value()
                    self.invoicesSales.descuento = self.descuentoDoubleSpinBox.value()
                    self.invoicesSales.deuda = self.total - self.recibido
                    self.invoicesSales.total = self.total
                    self.invoicesSales.html()

                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "No ha seleccionado el cliente, si no existe en la base de datos "
                                                        "puede crearlo")
        # <> fin DialogPaymentLayout


        class DialogClientLayout(QDialog, dialogClientUi, SQL):
            def __init__(self, inicio=True):
                super(DialogClientLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.user = User()

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.loadTabla()

                self.isInicio = inicio

                self.connection()

            def connection(self):
                self.lineEditBuscar.textChanged.connect(self.buscar)
                self.treeWidgetClients.itemDoubleClicked.connect(self.clientSelect)
                self.newClientePushButton.clicked.connect(self.newClient)

            def loadTabla(self, QUERY=""):
                self.treeWidgetClients.clear()
                for i in self.clientQuery(SELECT="client", QUERY=QUERY):
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.treeWidgetClients.addTopLevelItem(item)

            def buscar(self, txt):
                if txt != "":
                    self.loadTabla(" AND lower(client) GLOB '*{}*'".format(txt.lower()))
                else:
                    self.loadTabla()

            def clientSelect(self, item):
                client = self.clientQuery(SELECT="client, phone, discount, address, email", QUERY=" AND client == '{}'".
                                          format(item.text(0)))
                self.client = client

                if not self.isInicio:
                    self.accept()
                else:
                    dialog = DialogNewClientLayout(not self.isInicio)
                    dialog.user = self.user.user
                    dialog.nombreLineEdit.setText(client[0][0])
                    dialog.telefonoLineEdit.setText(client[0][1])
                    dialog.descuentoDoubleSpinBox.setValue(client[0][2])
                    dialog.direccionLineEdit.setText(client[0][3])
                    dialog.emailLineEdit.setText(client[0][4])

                    dialog.nombreLineEdit.setReadOnly(True)
                    dialog.telefonoLineEdit.setReadOnly(True)
                    dialog.descuentoDoubleSpinBox.setReadOnly(True)
                    dialog.direccionLineEdit.setReadOnly(True)
                    dialog.emailLineEdit.setReadOnly(True)
                    if dialog.exec_():
                        pass

            def newClient(self):
                dialog = DialogNewClientLayout(True)
                if dialog.exec_():
                    self.lineEditBuscar.setText(dialog.nombreLineEdit.text())
        # <> fin DialogClientLayout


        class DialogList(QDialog, dialogListUi, SQL):
            def __init__(self, header, list, print=True, opcion=""):
                super(DialogList, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.opcion = opcion
                self.opcionInventario = "Inventario"
                self.opcionCategoria = "Categoria"
                self.opcionProveedor = "Proveedor"

                self.header = header
                self.loadTabla(header, list)

                if print:
                    self.printPushButton.hide()

                self.action = ""
                self.actionPrint = "print"

                self.connection()

            def connection(self):
                self.cancelPushButton.clicked.connect(self.cancel)
                self.printPushButton.clicked.connect(self.print)
                self.searchLineEdit.textChanged.connect(self.buscar)
                if self.opcion == self.opcionCategoria or self.opcion == self.opcionProveedor:
                    self.tablaTreeWidget.itemDoubleClicked.connect(self.opciones)

            def loadTabla(self, header, list):
                self.tablaTreeWidget.clear()
                self.tablaTreeWidget.setHeaderLabels(header)
                for i in list:
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    self.tablaTreeWidget.addTopLevelItem(item)

            def buscar(self, txt):
                text = re.compile(r"\w+")
                txt = text.findall(txt)
                if self.opcion == self.opcionInventario:
                    if len(txt) > 0:
                        txt = txt[0].lower()
                        query = ""
                        for i in ["Components.component", "Classify.codeCom", "Classify.codeFab"]:
                            query += " OR lower({}) GLOB '*{}*'".format(i, txt)
                        query = query[4:]
                        lista = self.classifyQuery(SELECT="Classify.location, Components.component, Classify.supplier, "
                                                          "Classify.codeCom, Classify.codeFab, Classify.cantAlm, "
                                                          "Classify.costProd, "
                                                          "round(Classify.cantAlm * Classify.costProd, 2)",
                                                   QUERY=" AND Classify.cantAlm > 0 AND ({}) GROUP BY Classify.id".
                                                   format(query))
                    else:
                        query = ""
                        for i in ["Components.component", "Classify.codeCom", "Classify.codeFab"]:
                            query += " OR lower({}) GLOB '*'".format(i)
                        query = query[4:]
                        lista = self.classifyQuery(SELECT="Classify.location, Components.component, Classify.supplier, "
                                                          "Classify.codeCom, Classify.codeFab, Classify.cantAlm, "
                                                          "Classify.costProd, "
                                                          "round(Classify.cantAlm * Classify.costProd, 2)",
                                                   QUERY=" AND Classify.cantAlm > 0 AND ({}) GROUP BY Classify.id".
                                                   format(query))
                    self.loadTabla(self.header, lista)
                elif self.opcion == self.opcionCategoria:
                    if len(txt) > 0:
                        txt = txt[0].lower()
                        lista = self.componetsQuery(QUERY=" AND lower(component) GLOB '*{}*'".format(txt))
                    else:
                        lista = self.componetsQuery(QUERY=" AND lower(component) GLOB '*'")
                    self.loadTabla(self.header, lista)
                elif self.opcion == self.opcionProveedor:
                    if len(txt) > 0:
                        txt = txt[0].lower()
                        lista = self.classifyQuery(SELECT="DISTINCT Classify.supplier",
                                                   QUERY=" AND lower(Classify.supplier) GLOB '*{}*' ".format(txt))
                    else:
                        lista = self.classifyQuery(SELECT="DISTINCT Classify.supplier",
                                                   QUERY=" AND lower(Classify.supplier) GLOB '*' ")
                    self.loadTabla(self.header, lista)

            def opciones(self, item):
                objecto = item.text(0)

                dialog = DialogOpcionLayout(("Editar", "Eliminar"))
                if dialog.exec_():
                    if dialog.action == dialog.actionEditar:
                        editar = QInputDialog()
                        editar.setWindowTitle("Editar")
                        editar.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                        editar.setLabelText("")
                        editar.setStyleSheet(style)
                        if editar.exec_():
                            __editar__ = editar.textValue()
                            if self.opcion == self.opcionCategoria:
                                self.componentUpdate(__editar__, objecto)
                                QMessageBox.information(self, "Informacion", "Categoría editada correctamente :)")
                            elif self.opcion == self.opcionProveedor:
                                self.supplierUpdate(__editar__, objecto)
                                QMessageBox.information(self, "Informacion", "Proveedor editado correctamente :)")
                            self.buscar("")
                    elif dialog.action == dialog.actionEliminar:
                        opcion = {
                            "Proveedor": ("al Proveedor", "este Proveedor"),
                            "Categoria": ("la Categoría", "esta Categoría"),
                        }
                        reply = QMessageBox.question(self, 'Confirmación Eliminación',
                                                     "¿Estás seguro que desea eliminar {} {}?\n"
                                                     "Esta operación eliminará los productos asociados a {} "
                                                     "y a su vez a todas las operaciones asociadas a esos productos".
                                                     format(opcion[self.opcion][0], objecto, opcion[self.opcion][1]),
                                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            if self.opcion == self.opcionCategoria:
                                if self.componentDelete(objecto):
                                    QMessageBox.information(self, "Aviso", "Categoría eliminada correctamente :)")
                                else:
                                    QMessageBox.critical(self, "Error", "No es posible eliminar esta categoría; "
                                                                        "porque tiene operaciones relacionadas, "
                                                                        "lo cual afecta directamente la contabilidad "
                                                                        "del sistema")
                            elif self.opcion == self.opcionProveedor:
                                if self.supplierDelete(objecto):
                                    QMessageBox.information(self, "Aviso", "Proveedor eliminado correctamente :)")
                                else:
                                    QMessageBox.critical(self, "Error", "No es posible eliminar esta categoría; "
                                                                        "porque tiene operaciones relacionadas, "
                                                                        "lo cual afecta directamente la contabilidad "
                                                                        "del sistema")
                            self.buscar("")

            def cancel(self):
                self.reject()

            def print(self):
                self.action = self.actionPrint
                self.accept()
        # <> fin DialogList


        class DialogNewClientLayout(QDialog, dialogNewClientUi, SQL):
            def __init__(self, editable=True):
                super(DialogNewClientLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.user = User()

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.editable = editable

                self.okPushButton.hide()

                if not self.editable:
                    self.facturaPushButton.show()
                else:
                    self.facturaPushButton.hide()

                self.connect()

            def connect(self):
                self.nombreLineEdit.textChanged.connect(self.nombre)
                self.okPushButton.clicked.connect(self.ok)
                self.cancelPushButton.clicked.connect(self.cancel)
                self.facturaPushButton.clicked.connect(self.showFacturas)

            def nombre(self, txt):
                if txt.__len__() > 5 and self.editable:
                    self.okPushButton.show()
                else:
                    self.okPushButton.hide()

            def ok(self):
                if self.clientInsert([self.nombreLineEdit.text(), self.direccionLineEdit.text(), self.telefonoLineEdit.text(),
                                      self.emailLineEdit.text(), str(self.descuentoDoubleSpinBox.value())]):
                    QMessageBox.information(self, "Aviso", "Cliente insertado correctamente !")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Cliente no pudo ser insertado :(")

            def cancel(self):
                self.reject()

            def showFacturas(self):
                dialog = DialogCalendarLayout()
                if dialog.exec_():
                    date = dialog.getDay()
                    fecha0 = datetime.date(year=date[0].year(), month=date[0].month(), day=date[0].day())
                    fecha1 = datetime.date(year=date[1].year(), month=date[1].month(), day=date[1].day())
                    lista = self.queryFree(SELECT="El.time, I.type, S.discount, round(D.dep - D.money, 2), S.total",
                                           FROM="EventsLog El, Invoices I, Clients Cl, Sales S, Debt D",
                                           QUERY="S.id_invoice == I.id AND S.id_client == Cl.id "
                                                 "AND D.id_client == Cl.id AND D.id_invoice == I.id "
                                                 "AND I.id_event == El.id_event AND El.time >= '{} 00:00:00' AND "
                                                 "El.time <= '{} 23:59:59' AND Cl.client == '{}'".
                                           format(fecha0.isoformat(),
                                                  fecha1.isoformat(),
                                                  self.nombreLineEdit.text()))
                    meta = self.queryFree(SELECT="round(sum(S.discount), 2), round(sum(D.dep - D.money), 2), "
                                                 "round(sum(S.total))",
                                          FROM="EventsLog El, Invoices I, Clients Cl, Sales S, Debt D",
                                          QUERY="S.id_invoice == I.id AND S.id_client == Cl.id "
                                                "AND D.id_client == Cl.id AND D.id_invoice == I.id "
                                                "AND I.id_event == El.id_event AND El.time >= '{} 00:00:00' AND "
                                                "El.time <= '{} 23:59:59' AND Cl.client == '{}' GROUP BY Cl.id".
                                          format(fecha0.isoformat(),
                                                 fecha1.isoformat(),
                                                 self.nombreLineEdit.text()))

                    if lista != []:
                        header = ["Fecha", "Factura", "Descuento", "Deuda", "Total"]
                        dialogList = DialogList(header, lista)
                        dialogList.setWindowTitle("Relacion de Facturas para {}".format(self.nombreLineEdit.text()))
                        try:
                            dialogList.textLabel.setText(
                                "Total: {}\t Descuento: {}\t Deuda: {}".format(meta[0][2], meta[0][0], meta[0][1]))
                        except:
                            dialogList.textLabel.setText(
                                "Total: {}\t Descuento: {}\t Deuda: {}".format(0.0, 0.0, 0.0))
                        if dialogList.exec_():
                            if dialogList.action == dialogList.actionPrint:
                                # Meta de la tabla: Cliente, Telef, Condicion, Descuento Total, Deuda Total, MO, MIS, Total
                                # Meta de la tabla detalle: Fecha, Factura, Descuento, Deuda, Subtotal
                                tablaDetalle = ""
                                for fecha, factura, descuento, deuda, subtotal in lista:
                                    tablaDetalle += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>". \
                                        format(fecha, factura, descuento, deuda, subtotal)

                                deuda = meta[0][1]
                                descuento = meta[0][0]
                                total = meta[0][2]

                                html = """
                                                <!DOCTYPE html>
    <html class="html" lang="es-ES">
    <head>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8"/>
        <meta name="keywords" content="hostal, turismo, cuba, habana, havana"/>
        <meta name="generator" content="2015.0.0.309"/>
        <title>Lodging Invoice/ Factura de Alojamiento</title>
        <!-- CSS -->
        <link rel="stylesheet" type="text/css" href="css/site_global.css?4052507572"/>
        <link rel="stylesheet" type="text/css" href="css/index.css?4191106610" id="pagesheet"/>
        <link rel="stylesheet" href="stylesheet.css">
        <script src="config.js"></script>
    </head>
    <body>
    <div class="clearfix" id="page"><!-- column -->
        <div class="clearfix colelem" id="pppu113"><!-- group -->
            <div class="clearfix grpelem" id="ppu113"><!-- column -->
                <div class="clearfix colelem" id="pu113"><!-- group -->
                    <div class="rounded-corners clearfix grpelem" id="u113"><!-- column -->
                        <div class="position_content" id="u113_position_content">
                            <div class="clearfix colelem" id="u115-4"><!-- content -->
                                <p>Concepto/Concept</p>
                            </div>
                            <div class="clearfix colelem" id="u116-6"><!-- content -->
                                <p>Relacion de facturas</p>
                                <p id="u116-4">Relationship of invoice</p>
                            </div>
                        </div>
                    </div>
                    <div class="rounded-corners grpelem" id="u285"><!-- simple frame --></div>
                </div>
                <div class="clearfix colelem" id="pu118"><!-- group -->
                    <div class="rounded-corners clearfix grpelem" id="u118"><!-- column -->
                        <div class="position_content" id="u118_position_content">
                            <div class="clearfix colelem" id="u119-4"><!-- content -->
                                <p>Factura/Invoice</p>
                            </div>
                            <div class="clearfix colelem" id="u120-4"><!-- content -->
                                <p>{invoice}</p>
                            </div>
                        </div>
                    </div>
                    <div class="rounded-corners grpelem" id="u286"><!-- simple frame --></div>
                </div>
                <div class="clearfix colelem" id="pu121"><!-- group -->
                    <div class="rounded-corners clearfix grpelem" id="u121"><!-- column -->
                        <div class="position_content" id="u121_position_content">
                            <div class="clearfix colelem" id="u122-4"><!-- content -->
                                <p>Fecha/Date</p>
                            </div>
                            <div class="clearfix colelem" id="u123-4"><!-- content -->
                                <p>{pubdate}</p>
                            </div>
                        </div>
                    </div>
                    <div class="rounded-corners grpelem" id="u287"><!-- simple frame --></div>
                </div>
                <div class="clearfix colelem" id="pu124"><!-- group -->
                    <div class="rounded-corners clearfix grpelem" id="u124"><!-- column -->
                        <div class="position_content" id="u124_position_content">
                            <div class="clearfix colelem" id="u125-4"><!-- content -->
                                <p>Usuario/User</p>
                            </div>
                            <div class="clearfix colelem" id="u126-4"><!-- content -->
                                <p>{user}</p>
                            </div>
                        </div>
                    </div>
                    <div class="rounded-corners grpelem" id="u288"><!-- simple frame --></div>
                </div>
            </div>
            <div class="clip_frame grpelem" id="u75"><!-- image -->
                <img class="block" id="u75_img" src="images/ledea auto air.png" alt="" width="166" height="75"/>
            </div>
            <div class="clearfix grpelem" id="pu81-16"><!-- column -->
                <div class="clearfix colelem" id="u81-16"><!-- content -->
                    <p id="u81-2"><span id="u81">Dirección</span></p>
                    <p>Avenida 15 edif 8023 entre 82 y 90</p>
                    <p>Reparto Guiteras, Habana del Este, La Habana, Cuba</p>
                    <p id="u81-8"><span id="u81-7">Teléfono</span></p>
                    <p>&nbsp;7-7662316</p>
                    <p id="u81-12"><span id="u81-11">Email</span></p>
                    <p>informacion@servidorcliente.com</p>
                </div>
                <div class="clearfix colelem" id="pu313-10"><!-- group -->
                    <div class="clearfix grpelem" id="u313-10"><!-- content -->
                        <p id="u313-2"><span id="u313">Developer</span></p>
                        <p id="u313-4">Josué Isai Hernández Sánchez</p>
                        <p id="u313-6">josueisaihs@gmail.com</p>
                        <p id="u313-8">+53 53861204</p>
                    </div>
                    <div class="clip_frame grpelem" id="u314"><!-- image -->
                        <img class="block" id="u314_img" src="images/logo%20elijosoft%20150.png" alt="" width="100%"
                             style="padding-top: 30%"/>
                    </div>
                    <div class="rounded-corners clearfix grpelem" id="u318"><!-- group -->
                        <div class="grpelem" id="u316"><!-- rasterized frame --></div>
                    </div>
                </div>
                <div class="clearfix colelem" id="pu313-10"><!-- group -->
                    <div class="clearfix grpelem" id="u313-10"><!-- content -->
                        <p id="u313-4">6ta Nº204 entre Fomento y Albear, Cerro, La Habana</p>
                        <p id="u313-6">ventas@softwaresinlimite.com</p>
                        <p id="u313-8">+53 56142378</p>
                    </div>
                    <div class="clip_frame grpelem" id="u314"><!-- image -->
                        <img class="block" id="u314_img" src="images/dossl.png" alt="" width="100%"
                             style="padding-top: 30%"/>
                    </div>
                    <div class="rounded-corners clearfix grpelem" id="u318"><!-- group -->
                        <div class="grpelem" id="u316"><!-- rasterized frame --></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="colelem" id="u277"><!-- simple frame --></div>
        <div class="clearfix colelem" id="u280-4"><!-- content -->
            <p>Productos/Products</p>
        </div>
        <div class="colelem" id="u273"><!-- custom html -->
            <table>
                <tr class="inicio">
                    <td>Cliente</td>
                    <td>Telef</td>
                    <td>Condicion</td>
                    <td>Descuento</td>
                    <td>Deuda</td>
                    <td>Mano Obra</td>
                    <td>Miscelanea</td>
                    <td>Total</td>
                </tr>
                <tr>
                    <td>{cliente}</td>
                    <td>{telef}</td>
                    <td>Efectivo</td>
                    <td>{descuento}</td>
                    <td>{deuda}</td>
                    <td>{mano_obra}</td>
                    <td>{miscelanea}</td>
                    <td class="total">{total}</td>
                </tr>
            </table>
        </div>
        <div class="colelem" id="u275"><!-- custom html -->
            <table>
                <tr class="inicio">
                    <td>Fecha</td>
                    <td>Factura</td>
                    <td>Descuento</td>
                    <td>Deuda</td>
                    <td>Subtotal</td>
                </tr>
                {tablaDetalle}
            </table>
        </div>
        <div class="clearfix colelem" id="pu278-7"><!-- group -->
            <div class="clearfix grpelem" id="u278-7"><!-- content -->
                <p id="u278-2">______________________</p>
                <p id="u278-4">Firma Cliente</p>
                <p>&nbsp;</p>
            </div>
            <div class="clearfix grpelem" id="u279-7"><!-- content -->
                <p id="u279-2">______________________</p>
                <p id="u279-4">Firma Usuario</p>
                <p>&nbsp;</p>
            </div>
        </div>
        <div class="clearfix colelem" id="pu325"><!-- group -->
            <div class="clearfix grpelem" id="u325"><!-- column -->
                <div class="position_content" id="u325_position_content">
                    <div class="clearfix colelem" id="u329-4"><!-- content -->
                        <p>Recibo de Venta/Sales Voucher</p>
                    </div>
                    <div class="clearfix colelem" id="pu326-7"><!-- group -->
                        <div class="clearfix grpelem" id="u326-7"><!-- content -->
                            <p id="u326-2">______________________</p>
                            <p id="u326-4">Firma Cliente</p>
                            <p>&nbsp;</p>
                        </div>
                        <div class="clearfix grpelem" id="u327-7"><!-- content -->
                            <p id="u327-2">______________________</p>
                            <p id="u327-4">Firma Usuario</p>
                            <p>&nbsp;</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="clearfix grpelem" id="u328-4"><!-- content -->
                <p>Relacion de facturas: {cliente} Periodo: {pubdate}</p>
            </div>
        </div>
        <div class="verticalspacer"></div>
    </div>
    </body>
    </html>""".format(
                                    invoice="-",
                                    pubdate="{} al {}".format(fecha0.isoformat(), fecha1.isoformat(), ),
                                    user=self.user,
                                    cliente=self.nombreLineEdit.text(),
                                    telef=self.telefonoLineEdit.text(),
                                    descuento=descuento,
                                    mano_obra=0.0,
                                    miscelanea=0.0,
                                    deuda=deuda,
                                    total=total,
                                    tablaDetalle=tablaDetalle,
                                )

                                with open(os.path.join("system", "templete", "index.html"), "w",
                                          encoding="UTF-8") as file:
                                    file.write(html)
                                    file.close()
                                os.startfile(os.path.join("system", "templete", "index.html"))
                    else:
                        QMessageBox.critical(self, "Aviso", "El cliente no ha realzado compras de {} a {}".
                                             format(fecha0.isoformat(), fecha1.isoformat(), ))
        # <> fin DialogNewClientLayout


        class DialogNewWorkerLayout(QDialog, dialogNewWorker, SQL):
            def __init__(self):
                super(DialogNewWorkerLayout, self).__init__()
                QDialog.__init__(self)
                SQL.__init__(self)
                self.setupUi(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.okPushButton.hide()

                self.connection()

            def connection(self):
                self.nombreLineEdit.textChanged.connect(self.nombreTextChanged)
                self.apellidosLineEdit.textChanged.connect(self.apellidosTextChanged)
                self.cILineEdit.textChanged.connect(self.cITextChanged)
                self.okPushButton.clicked.connect(self.ok)
                self.cancelarPushButton.clicked.connect(self.reject)

            def nombreTextChanged(self, txt):
                self.nombreLineEdit.setText(self.filtroName(txt))
                self.mostrarOk()

            def apellidosTextChanged(self, txt):
                self.apellidosLineEdit.setText(self.filtroName(txt))
                self.mostrarOk()

            def cITextChanged(self, txt):
                self.mostrarOk()

            def mostrarOk(self):
                if len(self.cILineEdit.text()) == 11 and len(self.nombreLineEdit.text()) >= 3 \
                        and len(self.apellidosLineEdit.text()) >= 3:
                    self.okPushButton.show()
                else:
                    self.okPushButton.hide()

            def filtroName(self, txt):
                newTxt = ""
                many = 0
                for i in txt:
                    if i.isalpha():
                        newTxt += i
                    if i == " " and many == 0:
                        newTxt += i
                        many += 1
                return newTxt.title()

            def ok(self):
                worker = Worker()
                worker.name = self.nombreLineEdit.text()
                worker.lastname = self.apellidosLineEdit.text()
                worker.ci = self.cILineEdit.text()
                worker.street = self.calleLineEdit.text()
                worker.city = self.municipioLineEdit.text()
                worker.state = self.provinciaLineEdit.text()
                worker.phone = self.casaLineEdit.text()
                worker.phoneOther = self.otroCasaLineEdit.text()
                worker.mobil = self.movilLineEdit.text()
                worker.mobilOther = self.otroMovilLineEdit.text()
                worker.email = self.emailLineEdit.text()

                if self.workerInsert(worker) != 0:
                    QMessageBox.information(self, "Aviso", "Trabajador insertado correctamente")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo insertar el trabajador")
        # <> fin DialogNewWorker


        class InicioLayout(QDialog, inicioUi, SQL):
            def __init__(self, user):
                super(InicioLayout, self).__init__()
                self.setupUi(self)
                SQL.__init__(self)

                self.user = user

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.m_iconSize = QSize(70, 70)
                self.listWidgetPicker.setIconSize(self.m_iconSize)
                self.listWidgetPicker.setMinimumHeight(self.m_iconSize.height() + 50)

                self.m_iconSize = QSize(100, 100)
                self.listWidgetPickerAction.setIconSize(self.m_iconSize)
                self.listWidgetPickerAction.setMinimumHeight(self.m_iconSize.height() + 50)

                self.listWidgetPickerNotification.setIconSize(self.m_iconSize)
                self.listWidgetPickerNotification.setMinimumHeight(self.m_iconSize.height() + 50)

                self.listWidgetPickerDeuda.setIconSize(self.m_iconSize)
                self.listWidgetPickerDeuda.setMinimumHeight(self.m_iconSize.height() + 50)

                self.connection()

                self.lineEditFastSearcher.setText(" ")
                self.lineEditFastSearcher.setText("")

                self.action = (
                    {"image": "ada&spiner_logo_caj.png", "action": "Caja", "detalle": "Para la venta de productos",
                     "win": SalesLayout(), "status": "trabajador"},
                    # {"image": "ada&spiner_logo_reorden.png", "action": "Reordenar", "detalle": "Para reordenar los productos",
                    #  "win": "", "status": "administrador"},
                    {"image": "ada&spiner_logo_inventario.png", "action": "Inventario", "detalle": "Relacion de todos los productos",
                     "win": "Inventario", "status": "administrador"},
                    {"image": "ada&spiner_logo_finz.png", "action": "Finanzas", "detalle": "Para el análisis de las finazas",
                     "win": DialogFinanzasLayout(), "status": "administrador"},
                    {"image": "ada&spiner_logo_new_client.png", "action": "Clientes", "detalle": "Para consultar y editar usuarios",
                     "win": DialogClientLayout(), "status": "administrador"},
                    {"image": "ada&spiner_logo_new_prod.png", "action": "Productos", "detalle": "Para agregar nuevos productos",
                     "win": ProductLayout(), "status": "administrador"},
                    {"image": "ada&spiner_logo_busc.png", "action": " Buscador", "detalle": "Para buscar los productos",
                     "win": SearcherLayout(), "status": "administrador"},
                    {"image": "ada&spiner_logo_new_user.png", "action": "Perfiles", "detalle": "Para crear usuarios y permisos",
                     "win": Account(), "status": "administrador"},
                    {"image": "ada&spiner_logo_worker.png", "action": "Trabajadores", "detalle": "Para el control de los trabajadores",
                     "win": DialogNewWorkerLayout(), "status": "administrador"},
                    )
                for i in self.action:
                    if i["status"] == self.user.status.lower() or i["action"] == "Caja":
                        item = QListWidgetItem()
                        item.setIcon(QIcon(os.path.join("system", "image", i["image"])))
                        item.setText(i["action"] + "\n" + i["detalle"])
                        item.setToolTip(i["detalle"])
                        self.listWidgetPickerAction.addItem(item)

                if self.user.isAdmin():
                    for i in self.classifyQuery(SELECT="Classify.codeFab, Classify.codeCom, Classify.cantAlm",
                                                QUERY="AND Classify.cantAlm <= Classify.cantMin "
                                                      "ORDER BY Classify.cantVisit DESC"):
                        item = QListWidgetItem()
                        item.setIcon(QIcon(os.path.join("system", "image", "comprar_info.png")))
                        item.setText("Codigo: {}\nModelo: {}\n".format(i[0], i[1]))
                        self.listWidgetPickerNotification.addItem(item)

                self.loadListWidgetPickerDeuda()

                self.masterSecureAgent = ElijoSoftSecure()

                self.masterSecureTimer = QTimer()
                self.masterSecureTimer.timeout.connect(self.masterSecureTimerOut)
                self.masterSecureTimer.start(10000)
                # Es necesario Ejecutarlo Primero
                self.masterSecureTimerOut()

            def connection(self):
                self.listWidgetPicker.itemDoubleClicked.connect(self.listWidgetPickerSearchDoubleClicked)
                self.listWidgetPickerAction.itemDoubleClicked.connect(self.listWidgetPickerActionDoubleClicked)
                self.listWidgetPickerDeuda.itemDoubleClicked.connect(self.listWidgetPickerDeudaDoubleClicked)
                self.lineEditFastSearcher.textChanged.connect(self.search)

            def search(self, tx):
                self.listWidgetPicker.clear()

                MAKE = re.compile(r"\w{2,30}")
                MAKE = MAKE.findall(tx)

                CODCOM = re.compile(r"([a-z]{1,2})(-\d{1,5}|-)", re.I)
                CODCOM = CODCOM.findall(tx)

                CODFAB = re.compile(r"([a-z]{1,2})(-\d{1,5}[a-z]{0,4}|-\d{1,4}|-)", re.I)
                CODFAB = CODFAB.findall(tx)

                _QUERY_CODCOM_ = ""
                if CODCOM.__len__() > 1:
                    for i in CODCOM:
                        _QUERY_CODCOM_ = _QUERY_CODCOM_.__add__(
                            "C.codeCom GLOB '*{}*' OR ".format("{}{}".format(i[0].upper(), i[1])))
                elif CODCOM.__len__() == 1:
                    _QUERY_CODCOM_ = _QUERY_CODCOM_.__add__("C.codeCom GLOB '*{}*' OR ".format("{}{}".
                                                                                               format(CODCOM[0][0].upper(),
                                                                                                      CODCOM[0][1])))
                _QUERY_CODCOM_ = _QUERY_CODCOM_[:-4]

                _QUERY_CODFAB_ = ""
                if CODFAB.__len__() > 1:
                    for i in CODFAB:
                        _QUERY_CODFAB_ = _QUERY_CODFAB_.__add__(
                            "C.codeFab GLOB '*{}*' OR ".format("{}{}".format(i[0].upper(), i[1])))
                elif CODFAB.__len__() == 1:
                    _QUERY_CODFAB_ = _QUERY_CODFAB_.__add__("C.codeFab GLOB '*{}*' OR ".format("{}{}".
                                                                                               format(CODFAB[0][0].upper(),
                                                                                                      CODFAB[0][1])))
                _QUERY_CODFAB_ = _QUERY_CODFAB_[:-4]

                _QUERY_CLASSIFY_ = ""
                if _QUERY_CODCOM_ != "":
                    _QUERY_CLASSIFY_ = _QUERY_CLASSIFY_.__add__(_QUERY_CODCOM_)

                if _QUERY_CODFAB_ != "":
                    _QUERY_CLASSIFY_ = _QUERY_CLASSIFY_.__add__(" OR {}".format(_QUERY_CODFAB_))

                _QUERY_MAKE_ = ""
                if MAKE.__len__() > 1:
                    for i in MAKE:
                        _QUERY_MAKE_ = _QUERY_MAKE_.__add__("(Ma.make GLOB '{make}*' OR Mo.model GLOB '{make}*') OR ".
                                                            format(make=i.upper()))
                elif MAKE.__len__() == 1:
                    _QUERY_MAKE_ = _QUERY_MAKE_.__add__("(Ma.make GLOB '{make}*' OR Mo.model GLOB '{make}*') OR ".
                                                        format(make=MAKE[0].upper()))
                _QUERY_MAKE_ = _QUERY_MAKE_[:-4]

                SELECT = "C.codeFab, C.codeCom, C.detail"

                QUERY_CLASSIFY = ""
                if _QUERY_CLASSIFY_ != "":
                    QUERY_CLASSIFY += " AND ({})".format(_QUERY_CLASSIFY_)

                QUERY_MAKE = ""
                if _QUERY_MAKE_ != "":
                    QUERY_MAKE += " AND ({})".format(_QUERY_MAKE_)

                count = 0
                count_fin = 9
                if QUERY_CLASSIFY != "" or QUERY_MAKE != "":
                    for i in self.spinerSearchQuery(SELECT, QUERY_CLASSIFY, QUERY_MAKE, LIMIT=count_fin):
                        count += 1
                        self.loadListWidgetPicker(i)
                        if count == count_fin:
                            break
                else:
                    for i in self.classifyQuery(SELECT="Classify.codeFab, Classify.codeCom, Classify.detail",
                                                QUERY=" AND Classify.codeCom GLOB '*' LIMIT {}".format(count_fin)):
                        count += 1
                        self.loadListWidgetPicker(i)
                        if count == count_fin:
                            break

            def loadListWidgetPickerDeuda(self):
                if self.user.isAdmin():
                    self.listWidgetPickerDeuda.clear()
                    for i in self.debtQuery():
                        item = QListWidgetItem()
                        item.setIcon(QIcon(os.path.join("system", "image", "deuda.png")))
                        item.setText("{client}\t\n {invoice}\n Debe: {dep}\n Pagado: {money}\n {date}\n".format(
                            date=i.date, client=i.client, dep=i.dep, money=i.money, invoice=i.invoice
                        ))
                        self.listWidgetPickerDeuda.addItem(item)

            def loadListWidgetPicker(self, i):
                img = i[0].lower()
                img = img.replace("-", "")
                item = QListWidgetItem()
                if os.path.exists(os.path.join("system", "media", "300px", "{}.jpg".format(img))):
                    item.setIcon(QIcon(os.path.join("system", "media", "300px", "{}.jpg".format(img))))
                else:
                    item.setIcon(QIcon(os.path.join("system", "media", "300px", "vacio.jpg")))
                text = "Code: {codigo}\nModel: {modelo}\n\n{detalle}...". \
                    format(codigo=i[0], modelo=i[1], detalle=i[2][:30])
                item.setText(text)
                self.listWidgetPicker.addItem(item)

            def listWidgetPickerActionDoubleClicked(self, item):
                for i in self.action:
                    if i["action"] + "\n" + i["detalle"] == item.text():
                        try:
                            i["win"].__init__()
                            i["win"].user = self.user
                            i["win"].exec_()
                            self.loadListWidgetPickerDeuda()
                        except:
                            if i["win"] == "Inventario":
                                inventario = Inventario()
                            else:
                                QMessageBox.information(self, "Información", "Esta opción no se encuentra disponible por ahora :(")

            def listWidgetPickerDeudaDoubleClicked(self, item):
                text = item.text().split("\n")
                max = float(text[2].split(":")[1]) - float(text[3].split(":")[1])

                dialog = QInputDialog()
                dialog.setWindowTitle("Amortizar")
                dialog.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                dialog.setLabelText("{}\n A pagar: {}".format(item.text(), max))
                dialog.setDoubleMaximum(max)
                dialog.setInputMode(QInputDialog.DoubleInput)
                dialog.setStyleSheet(style)
                if dialog.exec_():
                    if dialog.doubleValue() > 0:
                        debt = DebtDetalle()
                        debt.client = text[0].strip()
                        debt.invoice = text[1].strip()
                        debt.dep = float(text[2].split(":")[1])
                        debt.money = float(text[3].split(":")[1])
                        debt.date = text[4].strip()
                        debt.updateMoney(dialog.doubleValue())

                        self.debtUpdate(debt)

                        QMessageBox.information(self, "Aviso", "Deuda amortizada correctamente :(")

                        self.loadListWidgetPickerDeuda()

            def listWidgetPickerSearchDoubleClicked(self, item):
                if self.user.isAdmin():
                    dialog = DialogOpcionLayout(("Detalle", "Compra"))
                else:
                    dialog = DialogOpcionLayout(("Compra",))

                texto = item.text()
                code, model, _, __ = texto.split("\n")
                code = code.replace("Code: ", "")
                model = model.replace("Model: ", "")
                self.producto = ProductDetalle()
                self.producto.set_codFab(code)
                self.producto.set_codCom(model)

                if dialog.exec_():
                    if dialog.action == dialog.actionAdd:
                        self.updateProducto()
                        self.accept()
                    elif dialog.action == dialog.actionDetalle:
                        self.updateProducto()
                        detalle = DialogSelectLayout(self.producto)
                        detalle.exec_()
                    elif dialog.action == dialog.actionKardex:
                        self.updateProducto()
                        dialogKardex = QInputDialog()
                        dialogKardex.setWindowTitle("Compra")
                        dialogKardex.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                        dialogKardex.setLabelText("Code: {}\nModel: {}\nCant Alm: {}\n\nInsertar la cantidad agregada".
                                                  format(self.producto.get_codFab(), self.producto.get_codCom(),
                                                         self.producto.get_cantAlm()))
                        dialogKardex.setInputMode(QInputDialog.DoubleInput)
                        dialogKardex.setDoubleMaximum(1000)
                        dialogKardex.setStyleSheet(style)
                        if dialogKardex.exec_():
                            if dialogKardex.doubleValue() > 0:
                                try:
                                    invoiceKardex = InvoiceKardex()
                                    invoiceKardex.set_User(self.user.user)
                                    invoiceKardex.set_invoice(self.sequenceQuery("seq", "AND name == 'Invoices'")[0] + 1)
                                    invoiceKardex.kardex = float(dialogKardex.doubleValue())
                                    invoiceKardex.set_Id(self.producto.get_Id())
                                    invoiceKardex.set_costProd(self.producto.get_costProd())

                                    self.invoiceKardexInsert(invoiceKardex)

                                    self.producto.add_cantAlm(dialogKardex.doubleValue())
                                    self.classifyUpdate([self.producto])
                                    QMessageBox.information(self, "Información", "Compra realizado correctamente :)")
                                except Exception as e:
                                    print(e)
                                    QMessageBox.critical(self, "Error", "Compra no ejecutado\nReinicie el programa e "
                                                                        "intente la operación nuevamente :(")
                            else:
                                QMessageBox.warning(self, "Atención", "No se agregó ningún producto :(")

            def updateProducto(self):
                detalles = self.classifyQuery(
                    SELECT="Components.component, Classify.costProd, Classify.price1, Classify.price2, "
                           "Classify.price3, Classify.price4, Classify.cantAlm, Classify.supplier, "
                           "Classify.flete, Classify.location, Classify.cantMin, Classify.tax, "
                           "Classify.detail, Classify.fullbarcode, Classify.id",
                    QUERY=" AND Classify.codeCom == '{}' AND Classify.codeFab == '{}'".format(
                        self.producto.get_codCom(), self.producto.get_codFab()))[0]
                self.producto.set_category(detalles[0])
                self.producto.set_costProd(detalles[1])
                self.producto.set_price1(detalles[2])
                self.producto.set_price2(detalles[3])
                self.producto.set_price3(detalles[4])
                self.producto.set_price4(detalles[5])
                self.producto.set_cantAlm(detalles[6])
                self.producto.set_supplier(detalles[7])
                self.producto.set_flete(detalles[8])
                self.producto.set_location(detalles[9])
                self.producto.set_cantMin(detalles[10])
                self.producto.set_tax(detalles[11])
                self.producto.set_detail(detalles[12])
                self.producto.set_barcode(detalles[13])
                self.producto.set_Id(detalles[14])

            def masterSecureTimerOut(self):
                if not self.masterSecureAgent.validProgram():
                    QMessageBox.critical(self, "Error Fatal", "Hemos encontrado un error fatal en tu equipo\n"
                                                              "Se ha modificado la hora se necesita interrumpir "
                                                              "la ejecucion.\n"
                                                              "Pongase en contacto con el servicio tecnico")
                    self.close()

            def closeEvent(self, event):
                reply = QMessageBox.question(self, 'Confirmación Salida',
                                             "¿Estás seguro que desea salir?", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    event.accept()
                    sys.exit()
                else:
                    event.ignore()
        # <> fin InicioLayout


        class DialogCalendarLayout(QDialog, dialogCalendarioUi):
            def __init__(self, fecha=datetime.date.today(), text="Seleccione la fecha de inicio"):
                super(DialogCalendarLayout, self).__init__()
                self.setupUi(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.calendarWidget.setMinimumDate(datetime.date(year=2016, month=12, day=22))
                self.calendarWidget.setMaximumDate(fecha)
                self.calendarWidget.clicked.connect(self.calendar)
                self.calendarWidget.showToday()

                self.labelText.setText(text)
                self.dayIn = False
                self.day = ["-", "-"]

            def calendar(self, date):
                if not self.dayIn:
                    self.day[0] = date
                    self.dayIn = True
                    self.labelText.setText("Seleccione la fecha final")
                    self.calendarWidget.setMinimumDate(datetime.date(year=date.year(), month=date.month(), day=date.day()))
                else:
                    self.day[1] = date
                    self.dayIn = False
                    self.accept()

            def getDay(self):
                return self.day
        # <> fin DialogCalendar


        class Login(QDialog, loginUi, SQL):
            def __init__(self, inicio=True):
                super(Login, self).__init__()
                QDialog.__init__(self)
                SQL.__init__(self)
                self.setupUi(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.masterSecureAgent = ElijoSoftSecure()

                self.setWindowFlags(Qt.SplashScreen)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.inicio = inicio

                self.labelImagen.setStyleSheet("image: url('system/image/elijosoft.png')")
                self.labelLogin.setStyleSheet("image: url('system/image/login.png')")
                self.pushButtonLogin.clicked.connect(self.login)
                self.pushButtonAccountCreate.clicked.connect(self.account)

                self.frameLogin.hide()
                self.labelLogin.hide()

                self.labelImagen.move(self.geometry().width() / 2 - self.labelImagen.geometry().width() / 2,
                                      self.geometry().height() / 2 - self.labelImagen.geometry().height() / 2)

                self.frameLogin.move(self.geometry().width() / 2 - self.frameLogin.geometry().width() / 2,
                                     self.geometry().height() / 2 + 10)

                self.labelLogin.move(self.geometry().width() / 2 - self.labelLogin.geometry().width() / 2,
                                     self.geometry().height() / 2 - self.labelLogin.geometry().height() - 10)

                self.pushButtonLoginGeo = self.pushButtonLogin.geometry()
                self.pushButtonAccountCreateGeo = self.pushButtonAccountCreate.geometry()
                self.labelLoginGeo = self.labelLogin.geometry()

                self.loadSplash = QTimer()
                self.loadSplash.timeout.connect(self.loadSplashOut)
                self.loadSplash.start(100)

                self.animLogin = QTimer()
                self.animLogin.timeout.connect(self.animacionLogin)

                self.animAccount = QTimer()
                self.animAccount.timeout.connect(self.animacionAccount)

                self.animLabel = QTimer()
                self.animLabel.timeout.connect(self.animacionLabel)

            def masterSecure(self):
                if self.masterSecureAgent.validRequest():
                    is_valid, i = self.masterSecureAgent.validLic()
                    if is_valid:
                        p = ""
                        if i != 1 and i > 0:
                            p = "s"
                    else:
                        QMessageBox.information(self, "Licencia", "No tiene una licencia activa\n"
                                                                  "Genere un codigo de solicitud")
                        masterSecureLayout = ElijoSoftSecureLayout()
                        if masterSecureLayout.exec_():
                            pass
                else:
                    masterSecureLayout = ElijoSoftSecureLayout()
                    if masterSecureLayout.exec_():
                        pass

            def setInicio(self, inicio):
                self.inicio = inicio

            def animacionLogin(self):
                if self.pushButtonLogin.geometry().x() == self.pushButtonLoginGeo.x():
                    self.animLogin.stop()
                else:
                    self.pushButtonLogin.move(self.pushButtonLogin.geometry().x() - 1, self.pushButtonLogin.geometry().y())

            def animacionAccount(self):
                if self.pushButtonAccountCreate.geometry().x() == self.pushButtonAccountCreateGeo.x():
                    self.animAccount.stop()
                    self.animLogin.start(5)
                else:
                    self.pushButtonAccountCreate.move(self.pushButtonAccountCreate.geometry().x() - 1,
                                                      self.pushButtonAccountCreate.geometry().y())

            def animacionLabel(self):
                if self.labelLogin.geometry().y() == self.labelLoginGeo.y():
                    self.animLabel.stop()
                else:
                    self.labelLogin.move(self.labelLogin.geometry().x(),
                                                      self.labelLogin.geometry().y() - 1)

            def loadSplashOut(self):
                self.frameLogin.show()
                self.labelLogin.show()
                self.labelImagen.hide()

                self.pushButtonLogin.move(self.pushButtonLogin.geometry().x() + self.pushButtonLogin.geometry().width() + 10,
                                          self.pushButtonLogin.geometry().y())
                self.pushButtonAccountCreate.move(self.pushButtonAccountCreate.geometry().x() +
                                                  self.pushButtonAccountCreate.geometry().width() + 10,
                                                  self.pushButtonAccountCreate.geometry().y())
                self.labelLogin.move(self.labelLogin.geometry().x(),
                                     self.labelLogin.geometry().height())
                self.animAccount.start(5)
                self.animLabel.start(5)

                self.loadSplash.stop()

                self.masterSecure()

                if not self.inicio:
                    self.close()

            def keyPressEvent(self, event):
                if event.key() == Qt.Key_Return:
                    self.login()
                elif event.key() == Qt.Key_Escape:
                    self.close()

            def closeEvent(self, event):
                reply = QMessageBox.question(self, 'Confirmación Salida',
                                             "¿Estás seguro que desea salir?", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    event.accept()
                    sys.exit()
                else:
                    event.ignore()

            def login(self):
                try:
                    user, permission, name, lastname = self.loginUser(self.lineEditUser.text(), self.lineEditPwd.text())
                    if user:
                        self.hide()

                        user_ = User()
                        user_.user = user
                        user_.status = permission

                        admin = InicioLayout(user_)
                        admin.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
                        admin.exec_()
                    else:
                        self.lineEditUser.setText("")
                        self.lineEditPwd.setText("")
                except:
                    self.lineEditUser.setText("")
                    self.lineEditPwd.setText("")

            def account(self):
                # app = InicioLayout()
                # self.nextWindow.append(app)
                QMessageBox.information(self, "Aviso", "No disponible")
        # <> fin Login


        class DialogFinanzasLayout(QDialog, dialogFinanzasUi, SQL):
            def __init__(self):
                super(DialogFinanzasLayout, self).__init__()
                SQL.__init__(self)
                self.setupUi(self)

                self.user = User()

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.fecha0 = datetime.date.today() - datetime.timedelta(days=1)
                self.fecha1 = datetime.date.today()
                self.labelFecha.setText("Del {} al {}".format(self.fecha0.isoformat(), self.fecha1.isoformat()))
                self.loadFinanzas()

                self.connection()

            def connection(self):
                self.pushButtonFechasFinanzas.clicked.connect(self.fechasFinanzas)

            def loadFinanzas(self):
                self.loadKardex()
                self.loadSales()

                finanzas = self.finanzasQuery([self.fecha0.isoformat(), self.fecha1.isoformat()])

                self.llenarTreeWidget(self.libroMayorTreeWidget,
                                      finanzas.totalList,
                                      Qt.DescendingOrder)

                self.labelDebe.setText("Debe: $ {}".format(round(finanzas.debe, 2)))
                self.labelHaber.setText("Haber: $ {}".format(round(finanzas.haber, 2)))
                self.labelTotal.setText("Total: $ {}".format(round(finanzas.total, 2)))

            def loadKardex(self):
                self.llenarTreeWidget(self.kardexTreeWidget,
                                      self.kardexClassifyQuery(QUERY=" AND El.time >= '{} 00:00:00' AND El.time <= '{} 23:59:59' GROUP BY Ck.id_invoice".
                                                               format(self.fecha0.isoformat(), self.fecha1.isoformat())).
                                      kardexList, Qt.DescendingOrder)

            def loadSales(self):
                self.llenarTreeWidget(self.salesTreeWidget,
                                      self.salesClassifyQuery(QUERY=" AND El.time >= '{}' AND El.time <= '{}'".
                                                               format(self.fecha0.isoformat(), self.fecha1.isoformat())),
                                      Qt.DescendingOrder)

            def fechasFinanzas(self):
                fechas = DialogCalendarLayout()
                fechas.setWindowTitle("Período")
                if fechas.exec_():
                    date = fechas.getDay()
                    self.fecha0 = datetime.date(year=date[0].year(), month=date[0].month(), day=date[0].day())
                    self.fecha1 = datetime.date(year=date[1].year(), month=date[1].month(), day=date[1].day())
                    self.labelFecha.setText("Del {} al {}".format(self.fecha0.isoformat(), self.fecha1.isoformat()))
                    self.loadFinanzas()

            def llenarTreeWidget(self, widget, data, order):
                widget.clear()
                for i in data:
                    elem = []
                    for k in i:
                        elem.append(str(k))
                    item = QTreeWidgetItem(elem)
                    widget.addTopLevelItem(item)
                widget.sortItems(0, order)
        # <> fin DialogFinanzasLayout


        class Account(QDialog, dialogAccountUi, SQL):
            def __init__(self):
                super(Account, self).__init__()
                SQL.__init__(self)
                self.setupUi(self)

                self.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))

                self.labelUserError.hide()
                self.labelPWDError.hide()
                self.labelNameError.hide()
                self.labelLastNameError.hide()
                self.labelAccountCreate.hide()
                self.labelAccountCreateError.hide()
                self.labelPWDConf.hide()
                self.pushButtonAccountCreate.clicked.connect(self.account)

            def account(self):
                user = self.lineEditUser.text()
                pwd = self.lineEditPWD.text()
                pwdConf = self.lineEditPWDConf.text()
                permission = self.comboBoxPermission.currentText()
                name = self.lineEditName.text()
                lastname = self.lineEditLastName.text()

                if user != "" and name != "" and lastname != "" and pwd != "":
                    if pwd == pwdConf:
                        self.labelPWDConf.setStyleSheet('color: green;')
                        self.labelPWDConf.setText('Correct')
                        self.labelPWDConf.show()

                        user_ = User()
                        user_.user = user
                        user_.pwd = pwd
                        user_.status = permission
                        user_.name = name
                        user_.lastname = lastname
                        response = self.userInsert(user_)
                        if response:
                            self.labelAccountCreate.show()
                            self.labelAccountCreateError.hide()

                            self.lineEditUser.setText('')
                            self.lineEditPWD.setText('')
                            self.lineEditName.setText('')
                            self.lineEditLastName.setText('')
                        else:
                            self.labelAccountCreate.hide()
                            self.labelAccountCreateError.show()
                    else:
                        self.labelPWDConf.setStyleSheet('color: red;')
                        self.labelPWDConf.setText('Incorrect')
                        self.labelPWDConf.show()
                else:
                    self.labelUserError.show()
                    self.labelPWDError.show()
                    self.labelNameError.show()
                    self.labelLastNameError.show()
                    self.labelAccountCreate.hide()
                    self.labelAccountCreateError.show()
        # <> fin Account


        class Start:
          def __init__(self):
              app = QApplication(sys.argv)
              mainWin = Login()
              # mainWin = InicioLayout("josueisaihs")
              mainWin.show()
              mainWin.setWindowIcon(QIcon(os.path.join("system", "image", "icono.png")))
              sys.exit(app.exec_())
        # <> fin Start
    else:
        logging.warning("Problemas con el interprete de python %s", "INT001")
except:
    logging.warning("Error fatal %s", "ERR000")
