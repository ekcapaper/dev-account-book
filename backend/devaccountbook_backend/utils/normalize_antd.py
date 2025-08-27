import uuid

from devaccountbook_backend.schemas.domain import AccountEntryTreeNode

def normalize_to_children(obj):
    """
    APOC toJsonTree 결과를 받아서:
    - 모든 관계 배열 키를 children으로 통일
    - 각 노드에 key 필드를 추가 (id 있으면 그걸, 없으면 uuid)
    """
    if isinstance(obj, list):
        return [normalize_to_children(x) for x in obj]

    if isinstance(obj, dict):
        out = {}
        children = []
        for k, v in obj.items():
            if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                # 관계 배열 → children에 합치기
                children.extend(normalize_to_children(v))
            else:
                out[k] = normalize_to_children(v)

        # key 필드 강제 추가
        if "id" in out:
            out["key"] = str(out["id"])
        else:
            out["key"] = str(uuid.uuid4())

        if children:
            out["children"] = children
        return out

    return obj