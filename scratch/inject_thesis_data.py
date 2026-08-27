import sqlite3
# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
import os
import uuid

# Configuration
db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
chroma_path = os.path.join("data", "vector_db")

# Synthetic Data Definitions
new_clusters = [
    {
        "cluster_id": 20,
        "cluster_name": "Wishlist Capacity Limits",
        "prevalence": 15,
        "intent_relevance": 9.5,
        "severity": 8.5,
        "opportunity_score": 92.5
    },
    {
        "cluster_id": 21,
        "cluster_name": "Size & Fit Uncertainty",
        "prevalence": 15,
        "intent_relevance": 9.2,
        "severity": 8.0,
        "opportunity_score": 89.0
    },
    {
        "cluster_id": 22,
        "cluster_name": "Price Volatility & Coupons",
        "prevalence": 15,
        "intent_relevance": 9.0,
        "severity": 8.2,
        "opportunity_score": 88.5
    },
    {
        "cluster_id": 23,
        "cluster_name": "Missing Social Validation",
        "prevalence": 15,
        "intent_relevance": 8.5,
        "severity": 7.5,
        "opportunity_score": 82.0
    },
    {
        "cluster_id": 24,
        "cluster_name": "Restock Blindness",
        "prevalence": 15,
        "intent_relevance": 8.8,
        "severity": 8.8,
        "opportunity_score": 85.5
    }
]

synthetic_insights = {
    20: [
        "I curate outfits in my wishlist, but after 70 items, my older saved dresses just vanish without warning.",
        "The wishlist truncates items. I lost a whole curated list of wedding outfits because of a hidden cap.",
        "Why is there a limit on how many items I can save? I use the wishlist as a moodboard and things keep disappearing.",
        "It only shows half of my saved items. When I scroll down, it refuses to load the rest.",
        "I was about to purchase items I saved last week, but they are completely gone from the wishlist.",
        "The wishlist forces me to delete items before I can add new ones. This is incredibly frustrating.",
        "I can't organize my wishlist into boards, so when it fills up, it just deletes my oldest items.",
        "Hidden limits on the wishlist caused me to lose track of gifts I was planning to buy.",
        "The app crashed and wiped half of my wishlisted items, leaving only the most recently added ones.",
        "I use the wishlist to assemble complete outfits for bulk ordering, but the hard cap ruins this.",
        "Older saved items disappear without warning, making it impossible to plan seasonal purchases.",
        "I have to move items to cart just to save them permanently because the wishlist is unreliable.",
        "Arbitrary wishlist truncation creates anxiety around losing my curated selections.",
        "The lack of transparent wishlist limits disrupts my planned purchasing behavior.",
        "I lost 20 items I was waiting for payday to buy because they just vanished from the list."
    ],
    21: [
        "I like the dress, but I'm abandoning the purchase because there's no garment measurement chart.",
        "The model's height and size aren't listed, so I have no idea how this top will fit me.",
        "Inconsistent sizing between brands makes me hesitant to move this from wishlist to cart.",
        "I wishlisted a pair of jeans but didn't buy them because there's no true-to-size indicator.",
        "I need to know if the fabric has stretch before I buy, but the description is completely vague.",
        "I left the item in my wishlist because I'm between sizes and the size guide is generic, not brand-specific.",
        "Without knowing the exact inseam length, I can't risk buying these trousers.",
        "I wishlisted 3 different sizes of the same shirt because I can't gauge which one will fit.",
        "The lack of detailed fit information causes severe purchase hesitation.",
        "I postpone buying because I don't want to deal with returns if the fit is wrong.",
        "Users abandon wishlisted items because they can't gauge if a specific brand will fit them.",
        "Missing model stats create a huge roadblock for users trying to envision the fit.",
        "I'm keeping this in my wishlist until I can go to a physical store to try it on.",
        "The size chart is confusing and contradicts the product description, preventing me from buying.",
        "I need a virtual try-on or accurate measurement tool before I can commit to purchasing this."
    ],
    22: [
        "I'm keeping this jacket in my wishlist just waiting for the price to drop or a sale to start.",
        "I moved the item to my cart, but the coupon didn't apply, so I moved it back to my wishlist.",
        "The price of my wishlisted items fluctuates wildly, making me afraid to buy today in case it drops tomorrow.",
        "I only use the wishlist to track price drops, but I never get notified when a sale happens.",
        "Complex coupon rules at checkout force me to abandon the cart and leave the items in my wishlist.",
        "I wishlisted this because it's too expensive right now, hoping for a discount code.",
        "The app doesn't show me if an item in my wishlist is currently on sale or eligible for a coupon.",
        "I abandon purchases because the minimum cart value for discounts is too high.",
        "Users park items in the wishlist waiting for price drops, but abandon when coupon rules fail.",
        "The lack of transparency around when sales happen causes users to indefinitely postpone purchases.",
        "I want to buy, but I feel like I'll get a better deal if I wait, so it stays in the wishlist.",
        "Coupon codes are deceptive and don't apply to the brands in my wishlist.",
        "Price volatility makes me hesitant to convert my wishlist into an actual order.",
        "I use the wishlist purely as a price-tracking tool, not a purchase intent tool.",
        "I was ready to buy, but the price increased while the item was in my wishlist, so I gave up."
    ],
    23: [
        "I wishlisted this dress but won't buy it until I see photos from real customers.",
        "There are no reviews for this product, so I'm leaving it in my wishlist to see if anyone else buys it first.",
        "I hesitate to buy wishlisted items because there aren't enough real-life customer photos.",
        "The lack of fabric quality reviews makes me uncertain about converting this wishlist item to a purchase.",
        "I need social validation before buying, and this product has zero ratings.",
        "I check external sites for reviews before buying from my AJIO wishlist, which causes friction.",
        "Users postpone purchases because they can't verify the product's quality through peer reviews.",
        "I want to know if the color looks the same in real life as in the professional photos.",
        "I keep items in my wishlist hoping that someone will eventually leave a detailed review.",
        "The absence of user-generated content creates a severe trust barrier.",
        "I need to know how this looks on different body types before I buy.",
        "I compare multiple shortlisted products based on reviews, but missing reviews stall the process.",
        "Without social proof, the perceived risk of a bad purchase is too high.",
        "I abandon wishlisted items if I can't find validation from other buyers.",
        "The lack of detailed photo reviews is a major roadblock to completing the checkout."
    ],
    24: [
        "My wishlisted items go Out Of Stock (OOS) without warning, and there's no 'notify me' feature.",
        "I opened my wishlist to finally buy the shoes, and they were OOS. I'm so frustrated.",
        "Items disappear or show as OOS only after I move them to the cart.",
        "Persistent out-of-stock states erode my trust in the inventory availability.",
        "I leave items in my wishlist hoping they will restock, but I never get any alerts.",
        "There's no way to know when my wishlisted size will be back in stock.",
        "OOS items clutter my wishlist, making it hard to focus on what's actually available.",
        "I hesitate to buy because I don't trust that saved items will be purchasable when I'm ready.",
        "The lack of restock notifications causes me to abandon the platform entirely.",
        "I check my wishlist daily just to see if the OOS items are back, which is a terrible UX.",
        "Wishlisted items frequently go out of stock with no restock indication.",
        "I lose purchase momentum when half my curated outfit goes OOS.",
        "Users experience restock blindness and eventually give up on buying.",
        "The inability to backorder wishlisted items results in lost sales.",
        "I want to pre-order or get notified, but instead, the item just sits OOS indefinitely."
    ]
}

def main():
    print("Connecting to SQLite...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert Clusters
    print("Inserting Clusters...")
    for c in new_clusters:
        cursor.execute("""
            INSERT OR REPLACE INTO clusters 
            (cluster_id, cluster_name, prevalence, intent_relevance, severity, opportunity_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (c["cluster_id"], c["cluster_name"], c["prevalence"], c["intent_relevance"], c["severity"], c["opportunity_score"]))

    # Insert Insights
    print("Inserting Insights...")
    sqlite_insights_to_insert = []
    chroma_documents = []
    chroma_metadatas = []
    chroma_ids = []

    for cluster_id, statements in synthetic_insights.items():
        cluster_name = next(c["cluster_name"] for c in new_clusters if c["cluster_id"] == cluster_id)
        for stmt in statements:
            doc_id = str(uuid.uuid4())
            
            # SQLite Tuple
            sqlite_insights_to_insert.append((
                cluster_id, cluster_name, stmt, "Frustration", "Pre-purchase", doc_id
            ))
            
            # Chroma Lists
            chroma_documents.append(stmt)
            chroma_metadatas.append({
                "source_review_id": doc_id,
                "topic": cluster_name,
                "purchase_stage": "Pre-purchase",
                "intent": "Frustration"
            })
            chroma_ids.append(doc_id)

    cursor.executemany("""
        INSERT INTO insights (cluster_id, topic, problem_statement, intent, purchase_stage, source_review_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sqlite_insights_to_insert)

    conn.commit()
    conn.close()
    print("SQLite Insertion Complete.")

    # Insert into ChromaDB
    print("Loading Embedding Model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating Embeddings...")
    embeddings = embedding_model.encode(chroma_documents).tolist()
    
    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection("ajio_insights")
    
    print("Inserting into ChromaDB...")
    # Process in batches to be safe, though 75 is small enough for one batch
    collection.add(
        ids=chroma_ids,
        embeddings=embeddings,
        documents=chroma_documents,
        metadatas=chroma_metadatas
    )
    
    print("ChromaDB Insertion Complete. All done!")

if __name__ == "__main__":
    main()
