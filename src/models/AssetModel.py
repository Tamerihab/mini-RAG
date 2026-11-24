from sqlalchemy import select

from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client =  db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == int(asset_project_id),
                    Asset.asset_type == asset_type
                )
                assets = await session.execute(query)
                return assets.scalars().all()

    async def get_asset_record(self, asset_project_id: str, asset_name: str) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == int(asset_project_id),
                    Asset.asset_name == asset_name
                )
                asset_record = await session.execute(query)
                return asset_record.scalar_one_or_none()

    async def get_asset_record_by_id(self, asset_project_id: str, asset_id: str) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == int(asset_project_id),
                    Asset.asset_id == int(asset_id)
                )
                asset_record = await session.execute(query)
                return asset_record.scalar_one_or_none()
