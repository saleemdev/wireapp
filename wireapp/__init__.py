__version__ = "0.0.1"

from librouteros import connect
import frappe


def test_conn():
    docname = "Terry Ian"
    update_internet_customer_account(docname, disabled=False)


@frappe.whitelist()
def update_internet_customer_account(docname, disabled=True):
    disabled = isinstance(disabled, bool)
    connection_deets = frappe.db.get_value(
        "Customer", docname, ["default_router", "address_id_"], as_dict=1
    )
    network_router = frappe.get_doc(
        "Network Router", connection_deets.get("default_router")
    )
    payload = dict(
        default_router=connection_deets.get("default_router"),
        host=network_router.get("host"),
        port=network_router.get("port"),
        username=network_router.get("username"),
        password=network_router.get("password"),
        address=connection_deets.get("address_id_"),
    )
    # print(payload)
    # return
    return client_actions(docname=docname, disabled=disabled, **payload)


def client_actions(docname=None, disabled=True, **connection_details):
    api = None
    # connection_details = connection_details.__dict__
    if connection_details.get("port"):
        api = connect(
            username=connection_details.get("username"),
            password=connection_details.get("password"),
            host=connection_details.get("host"),
            port=connection_details.get("port"),
            timeout=60,
        )
    else:
        api = connect(
            username=connection_details.get("username"),
            password=connection_details.get("password"),
            host=connection_details.get("host"),
            timeout=60,
        )
    if not api:
        return
    ips = api.path("ip", "address")

    client_network_id = list(
        filter(
            lambda x: x.get("address") == connection_details.get("address"), list(ips)
        )
    )[0]

    params = {"disabled": disabled, ".id": client_network_id.get(".id")}

    ips.update(**params)

    actioned = "Disconnected" if disabled else "Connected"

    frappe.msgprint(
        "{0} IP Address {1} on router [{2}] ".format(
            actioned,
            connection_details.get("address"),
            connection_details.get("default_router"),
        )
    )

    return actioned


@frappe.whitelist()
def update_customer_list(docname):
    frappe.get_doc("Network Router", docname).create_customers()
    return
@frappe.whitelist()
def add_customer_to_router(router, customer_name, address, interface):
    doc = frappe.get_doc("Network Router", router)
    params = dict(interface=interface, address=address,disabled=True,comment=customer_name)
    doc.add_customer_to_router(**params)
    frappe.msgprint("Assigned customer {0} IP address {1} on {2}. Customer Internet will be automatically activated upon payment of Invoice shared to the client".format(customer_name,address,interface))
    pass
@frappe.whitelist()
def get_router_interfaces(router):
    # router = "Kiptagich House Router"
    connection = frappe.get_doc("Network Router", router).get_connection()
    # First create desired path.
    interfaces = connection.path('interface')

    return ([x.get("name") for x in list(interfaces) if x.get("disabled")==False])

    #print([x.get("name") for x in list(interfaces)])