from dejavu import Dejavu

# Database configuration
config = {
    "database": {
        "host": "localhost",
        "user": "root",
        "password": "password",
        "database": "dejavu",
    },
    "database_type": "mysql",
}

# Initialize Dejavu
djv = Dejavu(config)

# Remove all songs and fingerprints from the database
djv.db.empty()
print(f"Total fingerprints in DB before processing: {djv.db.get_num_fingerprints()}")
