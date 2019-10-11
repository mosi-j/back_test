from my_database_info import get_database_info, vps1_remote_access, server_lan_access
from my_database_info import website_data, tsetmc_and_analyze_data

web_order_db_info = get_database_info(vps1_remote_access, website_data)
analyze_db_info = get_database_info(vps1_remote_access, tsetmc_and_analyze_data)

status_folder_name = '.single_server_status'
status_file_profix = 'btss'

# BackTestMultiProcessServer
back_test_multi_process_server_max_process_count = 1
back_test_multi_process_server_process_max_thread = 10
back_test_multi_process_server_process_order_avg_run_time = 60 * 0.1
back_test_multi_process_server_cycle_time = 6
back_test_multi_process_server_process_name = 'server_1'