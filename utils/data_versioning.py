"""
Data Versioning and Backup Strategy Module
Provides data versioning, backup, and recovery capabilities
"""

import os
import json
import shutil
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DataVersioningManager:
    """Manages data versioning and backup strategy"""
    
    def __init__(self, backup_dir: str = "backups", max_versions: int = 10):
        self.backup_dir = Path(backup_dir)
        self.max_versions = max_versions
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.backup_dir / "daily").mkdir(exist_ok=True)
        (self.backup_dir / "weekly").mkdir(exist_ok=True)
        (self.backup_dir / "monthly").mkdir(exist_ok=True)
        
        logger.info(f"✅ DataVersioningManager initialized: {backup_dir}")
    
    def create_backup(self, data: Dict[str, Any], source: str, 
                     backup_type: str = "daily") -> str:
        """Create a new backup version"""
        try:
            # Generate timestamp and hash
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_hash = self._calculate_hash(data)
            
            # Create backup filename
            filename = f"{source}_{timestamp}_{data_hash[:8]}.json"
            backup_path = self.backup_dir / backup_type / filename
            
            # Prepare backup metadata
            backup_data = {
                'metadata': {
                    'source': source,
                    'timestamp': timestamp,
                    'type': backup_type,
                    'hash': data_hash,
                    'version': self._get_next_version(source)
                },
                'data': data
            }
            
            # Save backup
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"✅ Backup created: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups(source, backup_type)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of data for integrity checking"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _get_next_version(self, source: str) -> int:
        """Get next version number for source"""
        existing_backups = self.list_backups(source)
        if not existing_backups:
            return 1
        return max(b.get('metadata', {}).get('version', 0) for b in existing_backups) + 1
    
    def _cleanup_old_backups(self, source: str, backup_type: str) -> None:
        """Remove old backups keeping only max_versions"""
        try:
            backup_path = self.backup_dir / backup_type
            backups = sorted(
                [f for f in backup_path.glob(f"{source}_*.json")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old backups
            for old_backup in backups[self.max_versions:]:
                old_backup.unlink()
                logger.info(f"🗑️  Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Backup cleanup warning: {e}")
    
    def list_backups(self, source: Optional[str] = None, 
                    backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available backups"""
        try:
            backups = []
            
            # Determine search paths
            if backup_type:
                search_paths = [self.backup_dir / backup_type]
            else:
                search_paths = [
                    self.backup_dir / "daily",
                    self.backup_dir / "weekly", 
                    self.backup_dir / "monthly"
                ]
            
            for path in search_paths:
                if not path.exists():
                    continue
                    
                for backup_file in path.glob("*.json"):
                    try:
                        with open(backup_file, 'r') as f:
                            backup_data = json.load(f)
                            
                        # Filter by source if specified
                        if source and backup_data.get('metadata', {}).get('source') != source:
                            continue
                            
                        backups.append(backup_data)
                        
                    except Exception as e:
                        logger.warning(f"Error reading backup {backup_file}: {e}")
            
            # Sort by timestamp (newest first)
            backups.sort(
                key=lambda x: x.get('metadata', {}).get('timestamp', ''), 
                reverse=True
            )
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_path: str, verify_hash: bool = True) -> Dict[str, Any]:
        """Restore data from backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Verify hash if requested
            if verify_hash:
                stored_hash = backup_data.get('metadata', {}).get('hash')
                current_hash = self._calculate_hash(backup_data.get('data', {}))
                
                if stored_hash != current_hash:
                    raise ValueError("Backup integrity check failed - hash mismatch")
            
            logger.info(f"✅ Backup restored: {backup_path}")
            return backup_data.get('data', {})
            
        except Exception as e:
            logger.error(f"❌ Backup restoration failed: {e}")
            raise
    
    def get_latest_backup(self, source: str) -> Optional[Dict[str, Any]]:
        """Get the most recent backup for a source"""
        backups = self.list_backups(source)
        return backups[0] if backups else None
    
    def create_scheduled_backups(self, data_sources: Dict[str, Any]) -> Dict[str, str]:
        """Create scheduled backups for multiple data sources"""
        results = {}
        timestamp = datetime.now()
        
        for source_name, data in data_sources.items():
            try:
                # Determine backup type based on schedule
                if timestamp.day == 1:  # First day of month
                    backup_type = "monthly"
                elif timestamp.weekday() == 0:  # Monday
                    backup_type = "weekly"
                else:
                    backup_type = "daily"
                
                backup_path = self.create_backup(data, source_name, backup_type)
                results[source_name] = backup_path
                
            except Exception as e:
                logger.error(f"Scheduled backup failed for {source_name}: {e}")
                results[source_name] = f"ERROR: {e}"
        
        return results
    
    def verify_backup_integrity(self, backup_path: str) -> bool:
        """Verify backup file integrity"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Check required fields
            if 'metadata' not in backup_data or 'data' not in backup_data:
                return False
            
            # Verify hash
            stored_hash = backup_data['metadata'].get('hash')
            current_hash = self._calculate_hash(backup_data['data'])
            
            return stored_hash == current_hash
            
        except Exception as e:
            logger.error(f"Backup integrity verification failed: {e}")
            return False

# Convenience functions
def create_backup(data: Dict[str, Any], source: str, backup_dir: str = "backups") -> str:
    """Create a simple backup"""
    manager = DataVersioningManager(backup_dir)
    return manager.create_backup(data, source)

def restore_latest(source: str, backup_dir: str = "backups") -> Optional[Dict[str, Any]]:
    """Restore the latest backup for a source"""
    manager = DataVersioningManager(backup_dir)
    latest = manager.get_latest_backup(source)
    
    if latest:
        backup_path = latest.get('metadata', {}).get('source', '')
        # Reconstruct path from metadata
        return manager.restore_backup(backup_path)
    
    return None

__all__ = ['DataVersioningManager', 'create_backup', 'restore_latest']
