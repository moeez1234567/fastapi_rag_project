# from qdrant_client import QdrantClient 
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from sentence_transformers import SentenceTransformer


# client = QdrantClient(host = "localhost", port=6333)

# query = "How do you find fossils?"

# model = SentenceTransformer("all-MiniLM-L6-v2")

# ende = model.encode(query).tolist()


# choice_1 = int(input("press 1 for seeing your question results")) 

# if choice_1 == 1:
#     results = client.search(
#         collection_name="company_b",
#         query_vector=ende,
#         limit=5,
#         with_payload=True, 
#         query_filter = Filter(must = [FieldCondition(key = "tenantid", match = MatchValue(value="company_a_book"))])
#     ) 

#     for r in results:
#         print(r.score)
#         print(r.payload)


# choice = int(input("Enter 0 for seeing the data : "))

# if choice == 0:
#     data, _ = client.scroll(
#     collection_name="company_b",
#     scroll_filter= Filter(must=[FieldCondition(key = "file", match=MatchValue(value = "company_a_book"))]),
#     limit=10,
#     with_vectors=True
# )   
#     for d in data:
#         print(d.payload.get("text")) 
# else:
#     print("how i help you : ")


from sentence_transformers import SentenceTransformer  

encode_model = SentenceTransformer("all-mpnet-base-v2")
encode_model.save("./app/all-mpnet-base-v2-local") 
print("model is save")