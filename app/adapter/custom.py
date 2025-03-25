from app.adapter.model import customer,Desk,DeskCustomer

#TODO: 待修改
# 外帶手機輸入登入,如果沒有顧客資訊新增
def create_customer(customer_name,customer_phone):
    new_customer = customer(customer_name=customer_name,customer_phone=customer_phone)
    return new_customer

# 內用客戶綁訂桌號
def create_desk_customer(desk_uuid, customer_uuid):
    new_desk_customer = DeskCustomer(desk_uuid=desk_uuid, customer_uuid=customer_uuid)
    return new_desk_customer