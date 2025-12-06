from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Cluster, User, ClusterFarmer
from fastapi import APIRouter, Depends, HTTPException, Request, Query , status
from ..database import get_db
from sqlalchemy import func
router = APIRouter(prefix="/cluster", tags=["creating a cluster "])
# ✅ Request Schema
# ✅ Pydantic schema
class ClusterCreate(BaseModel):
    location: str
    name: str
    farmer_name: str | None = None
    farmer_email: str | None = None
# class AddFarmerRequest(BaseModel):
#     cluster_id: int
#     farmer_name: str
#     farmer_email: str
class AddFarmerRequest(BaseModel):
    name: str               # cluster name instead of cluster_id
    farmer_name: str
    farmer_email: str

class MoveFarmerRequest(BaseModel):
    farmer_email: str
    from_cluster_name: str
    to_cluster_name: str

@router.post("/create", status_code=status.HTTP_201_CREATED)

@router.post("/create")
def create_cluster(payload: ClusterCreate, db: Session = Depends(get_db)):
    # prevent duplicates
    existing = (
        db.query(Cluster)
        .filter(Cluster.location == payload.location, Cluster.name == payload.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Cluster already exists")

    cluster = Cluster(name=payload.name, location=payload.location)
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    return {"message": "Cluster created", "cluster_id": cluster.id}

@router.post("/add-farmer", status_code=status.HTTP_201_CREATED)
def add_farmer_to_cluster(payload: AddFarmerRequest, db: Session = Depends(get_db)):
    # ✅ Step 1: Find the cluster by name
    cluster = db.query(Cluster).filter(Cluster.name == payload.name).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    # ✅ Step 2: Check cluster capacity (max 50)
    farmer_count = db.query(ClusterFarmer).filter(ClusterFarmer.cluster_id == cluster.id).count()
    if farmer_count >= 50:
        raise HTTPException(status_code=400, detail="Cluster already has 50 farmers")
    # ✅ Step 3: Check if farmer already exists in that cluster
    existing_farmer = (
        db.query(ClusterFarmer)
        .filter(
            ClusterFarmer.cluster_id == cluster.id,
            ClusterFarmer.farmer_email == payload.farmer_email
        )
        .first()
    )
    if existing_farmer:
        raise HTTPException(status_code=400, detail="Farmer already exists in this cluster")

    # ✅ Step 4: Check if farmer email exists in users table
    user = db.query(User).filter(User.email == payload.farmer_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Farmer not found in user table")

    # ✅ Step 5: Add farmer to the cluster
    farmer = ClusterFarmer(
        cluster_id=cluster.id,
        farmer_name=payload.farmer_name,
        farmer_email=payload.farmer_email
    )
    db.add(farmer)
    cluster.farmer_count += 1
    db.commit()
    db.refresh(cluster)

    return {
        "message": "Farmer added successfully",
        "cluster_name": cluster.name,
        "farmer_name": payload.farmer_name,
        "farmer_email": payload.farmer_email,
        "total_farmers": cluster.farmer_count
    }


@router.get("/{cluster_name}/farmers")
def get_farmers_by_cluster(cluster_name: str, db: Session = Depends(get_db)):
    cluster = db.query(Cluster).filter(Cluster.name == cluster_name).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    farmers = db.query(ClusterFarmer).filter(ClusterFarmer.cluster_id == cluster.id).all()

    return {
        "cluster_name": cluster.name,
        "location": cluster.location,
        "farmer_count": len(farmers),
        "farmers": [
            {
                "farmer_name": f.farmer_name,
                "farmer_email": f.farmer_email
            } for f in farmers
        ]
    }

@router.get("/all")
def get_all_clusters_with_farmers(db: Session = Depends(get_db)):
    # ✅ Step 1: Get all clusters
    clusters = db.query(Cluster).all()

    # ✅ Step 2: If no clusters
    if not clusters:
        return {"message": "No clusters found", "clusters": []}

    # ✅ Step 3: Build a structured response
    result = []
    for cluster in clusters:
        farmers = (
            db.query(ClusterFarmer)
            .filter(ClusterFarmer.cluster_id == cluster.id)
            .all()
        )

        result.append({
            "cluster_id": cluster.id,
            "cluster_name": cluster.name,
            "location": cluster.location,
            "farmer_count": cluster.farmer_count,
            "farmers": [
                {
                    "farmer_name": f.farmer_name,
                    "farmer_email": f.farmer_email
                }
                for f in farmers
            ]
        })

    return {
        "message": "Clusters retrieved successfully",
        "total_clusters": len(result),
        "clusters": result
    }


@router.post("/move-farmer")
def move_farmer(payload: MoveFarmerRequest, db: Session = Depends(get_db)):
    # ✅ Step 1: find both clusters
    from_cluster = db.query(Cluster).filter(Cluster.name == payload.from_cluster_name).first()
    to_cluster = db.query(Cluster).filter(Cluster.name == payload.to_cluster_name).first()

    if not from_cluster or not to_cluster:
        raise HTTPException(status_code=404, detail="One or both clusters not found")

    # ✅ Step 2: find farmer in the source cluster
    farmer = (
        db.query(ClusterFarmer)
        .filter(
            ClusterFarmer.cluster_id == from_cluster.id,
            ClusterFarmer.farmer_email == payload.farmer_email
        )
        .first()
    )

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found in source cluster")

    # ✅ Step 3: check capacity of destination cluster
    dest_farmer_count = db.query(ClusterFarmer).filter(ClusterFarmer.cluster_id == to_cluster.id).count()
    if dest_farmer_count >= 50:
        raise HTTPException(status_code=400, detail="Destination cluster is already full")

    # ✅ Step 4: ensure farmer isn’t already in the destination cluster
    existing_in_dest = (
        db.query(ClusterFarmer)
        .filter(
            ClusterFarmer.cluster_id == to_cluster.id,
            ClusterFarmer.farmer_email == payload.farmer_email
        )
        .first()
    )
    if existing_in_dest:
        raise HTTPException(status_code=400, detail="Farmer already exists in destination cluster")

    # ✅ Step 5: perform the move
    farmer.cluster_id = to_cluster.id
    from_cluster.farmer_count -= 1
    to_cluster.farmer_count += 1

    db.commit()
    db.refresh(from_cluster)
    db.refresh(to_cluster)

    return {
        "message": "Farmer moved successfully",
        "farmer_email": payload.farmer_email,
        "from_cluster": from_cluster.name,
        "to_cluster": to_cluster.name,
        "from_cluster_count": from_cluster.farmer_count,
        "to_cluster_count": to_cluster.farmer_count
    }




# def create_cluster(payload: ClusterCreate, db: Session = Depends(get_db)):
#     # ✅ Step 1: prevent duplicate cluster names in same location
#     existing = (
#         db.query(Cluster)
#         .filter(Cluster.location == payload.location, Cluster.name == payload.name)
#         .first()
#     )
#     if existing:
#         raise HTTPException(status_code=400, detail="Cluster name already exists for this location")
#
#     # ✅ Step 2: Verify farmer email or name exists in users table (if provided)
#     if payload.farmer_email or payload.farmer_name:
#         query = db.query(User)
#         if payload.farmer_email:
#             query = query.filter(User.email == payload.farmer_email)
#         elif payload.farmer_name:
#             query = query.filter(User.first_name == payload.farmer_name)
#         user = query.first()
#
#         if not user:
#             raise HTTPException(status_code=404, detail="Farmer not found in user table ")
#
#     # ✅ Step 3: Create cluster record
#     cluster = Cluster(
#         name=payload.name,
#         location=payload.location,
#         farmer_name=payload.farmer_name,
#         farmer_email=payload.farmer_email,
#         farmer_count=1 if payload.farmer_email else 0
#     )
#
#     db.add(cluster)
#     db.commit()
#     db.refresh(cluster)
#
#     return {
#         "message": "Cluster created successfully",
#         "cluster_id": cluster.id,
#         "cluster_name": cluster.name,
#         "location": cluster.location,
#         "farmer_email": cluster.farmer_email,
#         "farmer_name": cluster.farmer_name
#     }