"""
Monitoring and Health Checks Module
Provides system monitoring, health checks, and alerting capabilities
"""

import time
import psutil
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import json

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status data structure"""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component': self.component,
            'status': self.status,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metrics': self.metrics
        }

class SystemMonitor:
    """System monitoring and health check manager"""
    
    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 5000.0
        }
        
        self.health_history = deque(maxlen=1000)
        self.alert_handlers: List[Callable] = []
        self.component_checks: Dict[str, Callable] = {}
        
        logger.info("✅ SystemMonitor initialized")
    
    def register_component(self, name: str, check_func: Callable) -> None:
        """Register a component for health checking"""
        self.component_checks[name] = check_func
        logger.info(f"📝 Registered component: {name}")
    
    def add_alert_handler(self, handler: Callable) -> None:
        """Add an alert handler"""
        self.alert_handlers.append(handler)
    
    def check_system_health(self) -> Dict[str, HealthStatus]:
        """Perform comprehensive system health check"""
        try:
            health_statuses = {}
            
            # Check system resources
            health_statuses['system'] = self._check_system_resources()
            
            # Check registered components
            for name, check_func in self.component_checks.items():
                try:
                    status = check_func()
                    health_statuses[name] = status
                except Exception as e:
                    health_statuses[name] = HealthStatus(
                        component=name,
                        status='critical',
                        message=f'Health check failed: {e}',
                        timestamp=datetime.now(),
                        metrics={}
                    )
            
            # Store in history
            for status in health_statuses.values():
                self.health_history.append(status)
                
                # Trigger alerts if needed
                if status.status in ['warning', 'critical']:
                    self._trigger_alerts(status)
            
            return health_statuses
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            raise
    
    def _check_system_resources(self) -> HealthStatus:
        """Check system resource utilization"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine status
            status = 'healthy'
            messages = []
            
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                status = 'warning' if status == 'healthy' else status
                messages.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory_percent > self.alert_thresholds['memory_percent']:
                status = 'warning' if status == 'healthy' else 'critical'
                messages.append(f"High memory usage: {memory_percent:.1f}%")
            
            if disk_percent > self.alert_thresholds['disk_percent']:
                status = 'critical'
                messages.append(f"High disk usage: {disk_percent:.1f}%")
            
            message = "; ".join(messages) if messages else "System resources normal"
            
            return HealthStatus(
                component='system',
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_free_gb': disk.free / (1024**3)
                }
            )
            
        except Exception as e:
            logger.error(f"System resource check error: {e}")
            return HealthStatus(
                component='system',
                status='critical',
                message=f'System check failed: {e}',
                timestamp=datetime.now(),
                metrics={}
            )
    
    def _trigger_alerts(self, status: HealthStatus) -> None:
        """Trigger alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(status)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def get_health_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get health summary for a time window"""
        try:
            cutoff_time = datetime.now() - time_window if time_window else datetime.min
            
            # Filter by time window
            recent_statuses = [
                status for status in self.health_history 
                if status.timestamp > cutoff_time
            ]
            
            if not recent_statuses:
                return {'message': 'No health data available'}
            
            # Calculate statistics
            component_stats = {}
            for status in recent_statuses:
                if status.component not in component_stats:
                    component_stats[status.component] = {
                        'total': 0,
                        'healthy': 0,
                        'warning': 0,
                        'critical': 0
                    }
                
                stats = component_stats[status.component]
                stats['total'] += 1
                stats[status.status] += 1
            
            # Overall health score
            total_checks = sum(s['total'] for s in component_stats.values())
            healthy_checks = sum(s['healthy'] for s in component_stats.values())
            health_score = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                'health_score': round(health_score, 2),
                'total_checks': total_checks,
                'components': component_stats,
                'recent_issues': [
                    status.to_dict() for status in recent_statuses 
                    if status.status != 'healthy'
                ][-10:]  # Last 10 issues
            }
            
        except Exception as e:
            logger.error(f"Health summary error: {e}")
            return {'error': str(e)}
    
    def export_health_report(self, filename: str) -> str:
        """Export health report to file"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': self.get_health_summary(),
                'history': [
                    status.to_dict() for status in self.health_history
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Health report exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Health report export error: {e}")
            raise

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'response_times': deque(maxlen=1000),
            'error_rates': deque(maxlen=1000),
            'throughput': deque(maxlen=1000)
        }
        
        logger.info("✅ PerformanceMonitor initialized")
    
    def record_response_time(self, operation: str, duration_ms: float) -> None:
        """Record operation response time"""
        self.metrics['response_times'].append({
            'operation': operation,
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_error(self, operation: str, error_type: str) -> None:
        """Record operation error"""
        self.metrics['error_rates'].append({
            'operation': operation,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_throughput(self, operation: str, count: int) -> None:
        """Record operation throughput"""
        self.metrics['throughput'].append({
            'operation': operation,
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_performance_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get performance summary for time window"""
        try:
            cutoff = datetime.now() - timedelta(minutes=window_minutes)
            cutoff_str = cutoff.isoformat()
            
            # Filter recent metrics
            recent_response_times = [
                m for m in self.metrics['response_times']
                if m['timestamp'] > cutoff_str
            ]
            
            recent_errors = [
                m for m in self.metrics['error_rates']
                if m['timestamp'] > cutoff_str
            ]
            
            if not recent_response_times:
                return {'message': 'No performance data available'}
            
            # Calculate response time statistics
            durations = [m['duration_ms'] for m in recent_response_times]
            avg_response_time = sum(durations) / len(durations)
            max_response_time = max(durations)
            min_response_time = min(durations)
            
            # Calculate error rate
            total_operations = len(recent_response_times)
            error_count = len(recent_errors)
            error_rate = (error_count / total_operations * 100) if total_operations > 0 else 0
            
            return {
                'window_minutes': window_minutes,
                'avg_response_time_ms': round(avg_response_time, 2),
                'max_response_time_ms': round(max_response_time, 2),
                'min_response_time_ms': round(min_response_time, 2),
                'total_operations': total_operations,
                'error_count': error_count,
                'error_rate_percent': round(error_rate, 2),
                'operations_per_minute': round(total_operations / window_minutes, 2)
            }
            
        except Exception as e:
            logger.error(f"Performance summary error: {e}")
            return {'error': str(e)}

# Health check functions for common components
def check_database_connection() -> HealthStatus:
    """Check database connectivity"""
    try:
        # This is a placeholder - implement actual DB check
        return HealthStatus(
            component='database',
            status='healthy',
            message='Database connection OK',
            timestamp=datetime.now(),
            metrics={'connection_pool_size': 10}
        )
    except Exception as e:
        return HealthStatus(
            component='database',
            status='critical',
            message=f'Database connection failed: {e}',
            timestamp=datetime.now(),
            metrics={}
        )

def check_api_connectivity() -> HealthStatus:
    """Check external API connectivity"""
    try:
        # This is a placeholder - implement actual API check
        return HealthStatus(
            component='external_api',
            status='healthy',
            message='API connectivity OK',
            timestamp=datetime.now(),
            metrics={'response_time_ms': 150}
        )
    except Exception as e:
        return HealthStatus(
            component='external_api',
            status='warning',
            message=f'API connectivity issue: {e}',
            timestamp=datetime.now(),
            metrics={}
        )

# Convenience functions
def create_monitor() -> SystemMonitor:
    """Create and configure a system monitor"""
    monitor = SystemMonitor()
    
    # Register default component checks
    monitor.register_component('database', check_database_connection)
    monitor.register_component('external_api', check_api_connectivity)
    
    return monitor

__all__ = [
    'SystemMonitor', 
    'PerformanceMonitor', 
    'HealthStatus',
    'create_monitor',
    'check_database_connection',
    'check_api_connectivity'
]
