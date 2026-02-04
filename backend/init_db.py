from database import Base, engine
print("Initializing database tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
