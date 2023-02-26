import json


class SavePage:
    @staticmethod
    def process_item(item, spider):
        with open(f'saved_pages/page_{item["data"]["title"]}.html', 'w') as f:
            f.write(json.dumps(item['data']))
            f.close()
