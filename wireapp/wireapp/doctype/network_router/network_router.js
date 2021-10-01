// Copyright (c) 2021, Salim and contributors
// For license information, please see license.txt

frappe.ui.form.on('Network Router', {
	refresh(frm) {
		// your code here
		frm.add_custom_button(__("Refresh List"), function () {
			//perform desired action such as routing to new form or fetching etc.
			frm.dirty()
			frm.save()
		});
		frm.add_custom_button(__("Update Customer List"), function () {
			//perform desired action such as routing to new form or fetching etc.
			updateCustomerList(frm)
		});

		frm.add_custom_button(__("Add a New Customer"), function () {
			//perform desired action such as routing to new form or fetching etc.
			addNewUser(frm)
		});

	},


})
function updateCustomerList(frm) {
	frappe.call({
		"method": "wireapp.update_customer_list",
		args: {
			"docname": frm.doc.name
		}
	}).then(frappe.msgprint("Updated Customer List"))
}
function addNewUser(frm) {
	frappe.call({
		"method": "wireapp.get_router_interfaces",
		freeze: true,
		async: true,
		freeze_message: "Please wait as we pull active interfaces",
		args: {
			"router": frm.doc.name
		}

	}).then(res => {
		console.log(res)
		// prompt for multiple values
		frappe.prompt([
			{
				label: 'Customer Name',
				fieldname: 'customer_name',
				fieldtype: 'Data',
				reqd: 1,
			},
			{
				label: 'Address',
				fieldname: 'address',
				fieldtype: 'Data',
				reqd: 1,
			},
			{
				label: 'Interface',
				fieldname: 'interface',
				fieldtype: 'Select',
				reqd: 1,
				options: res.message
			},
		], (values) => {
			console.log(values.customer_name, values.address, values.interface);
			frappe.call({
				"method": "wireapp.add_customer_to_router",
				args: {
					router: frm.doc.name,
					customer_name: values.customer_name,
					address: values.address,
					interface: values.interface
				}
			}).then(console.log("Success..."))
		})
	})

}