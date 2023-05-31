class StatisticsManager:
    def __init__(self):
        self.statistics = {}

    def update_statistics(self, **kwargs):
        table_name, items = kwargs.popitem()

        if table_name not in self.statistics:
            self.statistics[table_name] = items
        else:
            self.statistics[table_name] += items

    def get_statistics(self):
        stats = ''
        for table_name, items in self.statistics.items():
            stats += f'VK_GEO: {items} items has been sent to {table_name}\n'

        return stats