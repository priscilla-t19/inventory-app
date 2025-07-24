import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool  # 👈 Required for transaction pooler

# Use the declarative base
Base = declarative_base()

# Supabase connection string from secrets.toml
DATABASE_URL = st.secrets["database"]["url"]

# Use NullPool to avoid keeping connections open (PgBouncer compatibility)
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},  # 👈 Supabase requires SSL
    poolclass=NullPool  # 👈 avoid connection reuse, required for PgBouncer
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- MODELS ---

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    item = Column(String)
    computer_name = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)
    make = Column(String)
    model = Column(String)
    screen_size = Column(String)
    man_serial_no = Column(String)
    g_serial_number = Column(String)
    operating_system = Column(String)
    os_version = Column(String)
    os_build = Column(String)
    system_type = Column(String)
    storage_size = Column(String)
    memory_size = Column(String)
    processor_speed = Column(String)
    office_suite = Column(String)
    comments = Column(String)
    recommendations = Column(String)
    location = Column(String)
    status = Column(String)
    date_of_purchase = Column(Date)
    cost = Column(String)
    supplier = Column(String)
    gpo_no = Column(String)
    warranty_period = Column(String)
    quantity = Column(Integer)
    storage_type = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

# --- INIT FUNCTION ---

def init_db():
    Base.metadata.create_all(bind=engine)


