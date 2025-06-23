import pandas as pd
import os

def save_results_to_excel(results, output_path):
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False)
    return output_path

def prepare_result_table(resume_info):
    result_table = []
    for item in resume_info:
        result_table.append({
            'name': item['name'],
            'email': item.get('email', 'N/A'),
            'phone': item.get('phone', 'N/A'),
            'score': item.get('score', 0),
            'missing_must': ", ".join(item.get('missing_must', [])) or "None",
            'missing_opt': ", ".join(item.get('missing_opt', [])) or "None",
            'missing_jd': item.get('missing_jd', "TBD"),
            'report': item.get('filename')
        })
    return result_table
