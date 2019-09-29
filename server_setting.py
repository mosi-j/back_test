
# from constant_database_data import laptop_web_order_db_info

from my_database_info import get_database_info, vps1_remote_access, website_data, tsetmc_and_analyze_data, server_lan_access


web_order_db_info = get_database_info(vps1_remote_access, website_data)
analyze_db_info = get_database_info(server_lan_access, tsetmc_and_analyze_data)
#web_order_db_info = laptop_web_order_db_info
