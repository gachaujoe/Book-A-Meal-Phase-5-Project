from flask import request

def paginate_query(query, page_size=10):
    page = request.args.get("page", 1, type=int)
    paginated = query.paginate(page, page_size, False)
    return {
        "items": [item.serialize() for item in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page,
    }
