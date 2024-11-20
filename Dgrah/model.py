import pydgraph
import json
import data_parser

def create_schema(client):
    schema = data_parser.CSV_Parser(client=client)
    schema.load_schema()
    
    
def create_data(client):
    data = data_parser.CSV_Parser(client=client)
    data.load_data("data")


def drop_all(client):
    drop = data_parser.CSV_Parser(client=client)
    drop.drop_all()
    
"""
    QUERY METHODS ACCORDING TO APP FUNCTIONALITY
"""

def query_menu(client):
    qm_options = {
        1: "Track content interactions for a given user",
        2: "analyze follower network",
        3: "get trending topics",
        4: "Generate user feed",
        5: "Get detailed performance metrics for posts",
        6: "Monitor community health metrics",
        7: "Calculate user influence scores",
        8: "Get personalized content recommendations",
        9: "Analyze user behavior patterns",
        10: "Forecast network growth",
        11: "Analyze content lifecycle patterns",
        12: "Exit"
    }
    for key in qm_options.keys():
        print(key, '--', qm_options[key])
        
    while True:
        option = int(input('Enter option: '))
        """ match option:
            case 1:
                track_content_interactions(client)
            case 2:
                analyze_follower_network(client)
            case 3:
                get_trending_topics(client)
            case 4:
                generate_user_feed(client)
            case 5:
                get_detailed_performance_metrics(client)
            case 6:
                monitor_community_health_metrics(client)
            case 7:
                calculate_user_influence_scores(client)
            case 8:
                get_personalized_content_recommendations(client)
            case 9:
                analyze_user_behavior_patterns(client)
            case 10:
                forecast_network_growth(client)
            case 11:
                analyze_content_lifecycle_patterns(client)
            case 12:
                break
            case _:
                print('Invalid option')
                query_menu(client) """

