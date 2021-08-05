free_proxy = [
                "193.27.23.150:9238",
                "194.33.29.71:7655",
                "185.102.50.7:7090",
                "45.154.228.33:8057",
                "37.35.42.252:8854",
                "45.130.128.149:9166",
                "37.35.40.102:8192",
                "91.246.193.186:6443",
                "185.242.94.92:6177",
                "193.27.21.131:8218",
                "109.207.130.163:8170",
                "2.56.101.122:8654",
                "2.56.101.181:8713",
                "2.56.101.253:8785",
                "2.56.101.250:8782",
                "2.56.101.4:8536",
              ]
# proxy_kamil = ["5.181.38.0:12323",
#                "5.181.38.1:12323",
#                "5.181.38.2:12323",
#                "5.181.38.3:12323",
#                "5.181.38.4:12323",
#                "5.181.38.5:12323",
#                "5.181.38.6:12323",
#                "5.181.38.7:12323"]
proxy_list = []

# for PROXY in proxy_kamil:
#     options = {
#         'proxy': {
#             'http': f'http://10aceb98ab147:873751dd9a@{PROXY}',
#             'https': f'https://10aceb98ab147:873751dd9a@{PROXY}',
#             'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
#         }
#     }
#     proxy_list.append(options)

for PROXY in free_proxy:
    options = {
        'proxy': {
            'http': f'http://lwdhxldm-dest:ey1qzygvm1z7@{PROXY}',
            'https': f'https://lwdhxldm-dest:ey1qzygvm1z7@{PROXY}',
            'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
        }
    }
    proxy_list.append(options)