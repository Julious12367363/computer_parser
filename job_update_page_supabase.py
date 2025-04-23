import json
import re
import time
from supabase_service import SupabaseService
from supabase import create_client, Client
from models import Links, Characteristics
from supabase_service import SupabaseService
from supabase_service import print_component_statistic

def main_():
    print()

if __name__ == "__main__":
    url = "https://market.yandex.ru//product--videokarta-asrock-amd-radeon-rx-6600-rx6600-clw-8g-8gb-challenger-gddr6-ret/868847027?hid=90401&sku=103645773421&show-uid=17403379099447944617516055&nid=26912670&from=search&cpa=1&do-waremd5=oyQmj2woj2c9qqF4aRygWw&cpc=-evkrX81I5b7TVk0PMiuTsMVt6mqLjJtJqQFpyAlBHSMM6TUQQiupOe2_dRDklreMCeYMBc71Gqk_MpuKl1p_bXyKzJKcetDgkuMUiFP99SDf0MjZhuT-kCbTqkBfpUoVQbFdyXlG28MbngCn44znMIYNWzPIAXBr29af1FXwC2UomWn7PUVeHNAUhTMnVAtHeMUZIIHuo5xaipeayEyxVNjTU6qBII7JywmyAlQdgtiDS3UaIUM6euQFy1k-vYA9o0HCW9TfO1srK44ts0ZC4EmLQUUBmvxHjlSnd6PZ-ZeBp7e4X9sk2PhLH5SNsvXhExk7T4Hhqe9CtG7hyYcPK98obwtGAQhhPTXRqqYrrGhT-NHXMO_wLOD--6Kip2g8JKSzzdXATfmQZfocH5JLhYE_cs-VeMLystVjDQUo2qm7_VS6Gt9bJsp4z0ZGqrV2pO68nBfFEU70mgkBZo06w%2C%2C&cc=CgAQB4B95u0G&uniqueId=858299"
    supabase_update = SupabaseService()
    data = supabase_update.get_link_by_url(url)
    print(data)
    #print()
    #all_links = supabase_update.get_links()
    #print(all_links)
    #update = supabase_update.insert_or_update_link()
    print_component_statistic(supabase_update.get_component_statistic())
    #print(supabase_update.materinskie_to_materinskay('materinskie-platy', 'materinskaia-plata'))
    #main()
