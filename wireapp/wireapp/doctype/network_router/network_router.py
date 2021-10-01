# Copyright (c) 2021, Salim and contributors
# For license information, please see license.txt

import frappe
from librouteros import connect
from frappe.model.document import Document


class NetworkRouter(Document):
	def get_connection(self):
		api = None
		if self.get("port"):
			api = connect(
				username=self.get("username"),
				password=self.get("password"),
				host=self.get("host"),
				port=self.get("port"),
				timeout=60,
		)
		else:
			api = connect(
				username=self.get("username"),
				password=self.get("password"),
				host=self.get("host"),
				timeout=60,
			)
		return api
	def before_save(self):
		if self.get("port"):
			api = connect(
				username=self.get("username"),
				password=self.get("password"),
				host=self.get("host"),
				port=self.get("port"),
				timeout=60,
			)
		else:
			api = connect(
				username=self.get("username"),
				password=self.get("password"),
				host=self.get("host"),
				timeout=60,
			)
		if not api:
			return
		ips = api.path("ip", "address")

		self.set("address_list", "{0}".format(list(ips)))
		self.client_addresses = []
		for addr in list(ips):
			row = self.append("client_addresses", {})
			row.id = addr.get(".id")
			row.ip_address = addr.get("address")
			row.network = addr.get("network")
			row.customer_name = addr.get("comment") or "-"
			row.disabled = addr.get("disabled")
	def add_customer_to_router(self, **params):
		api = self.get_connection()
		self.create_customers()
		if not api:
			return
		the_path = api.path("ip", "address")

		the_path.add(**params)
		
	def create_customers(self):
		for customer in list(filter(lambda x: x.get("customer_name")!='-',self.get("client_addresses"))):
			if not frappe.get_all(
				"Customer",
				filters=dict(address_id_=customer.get("ip_address")),
				fields=["*"],
			):
				status = "Disconnected" if customer.disabled else "Connected"
				args = dict(
					doctype="Customer",
					default_company = self.get("company"),
					customer_name=customer.get("customer_name"),
					address_id_=customer.get("ip_address"),
					default_router=self.get("name"),
					internet_status=status,
				)
				frappe.get_doc(args).insert(ignore_permissions=True)
				frappe.msgprint("Successfully created customer {0}".format(customer.get("customer_name")))


#
