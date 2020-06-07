from dataclasses import dataclass


@dataclass
class QueryMiddleWare:
    username: str = None
    since: str = None
    until: str = None
    query_search: str = None

    @property
    def query(self) -> str:
        query_list = []
        if self.username:
            query_list.append(f"from:{self.username}")
        if self.since:
            query_list.append(f"since:{self.since}")
        if self.until:
            query_list.append(f"until:{self.until}")
        if self.query_search:
            query_list.append(f"{self.query_search}")
        if not self.username and not self.query_search:
            raise
        temp_query = " ".join(query_list)
        if temp_query.strip() == "":
            raise
        else:
            return temp_query
