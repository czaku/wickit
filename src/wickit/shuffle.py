"""
wickit.shuffle - Port Management & Service Discovery

Auto-discover available ports, register mDNS services, and enable
frontend-backend service discovery for multi-tool architectures.

Usage:
    from wickit.shuffle import ServiceRegistry

    registry = ServiceRegistry(
        service_id="my-api",
        port_range=(7770, 7779),
        mdns_name="myapp.local"
    )

    port = registry.start()
    # Service now running with mDNS and health endpoint
"""

import socket
import json
from typing import Optional, Tuple, Dict, Any
from datetime import datetime


class PortShuffleError(Exception):
    """Base exception for port shuffle errors"""
    pass


class NoAvailablePortError(PortShuffleError):
    """Raised when no ports are available in the specified range"""
    pass


def find_available_port(port_range: Tuple[int, int]) -> int:
    """
    Find an available port within the specified range.

    Args:
        port_range: Tuple of (min_port, max_port) inclusive

    Returns:
        First available port number

    Raises:
        NoAvailablePortError: If no ports are available in range
    """
    min_port, max_port = port_range

    for port in range(min_port, max_port + 1):
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue

    raise NoAvailablePortError(
        f"No available ports in range {min_port}-{max_port}"
    )


class ServiceRegistry:
    """
    Register and manage a service with automatic port discovery and mDNS.

    Example:
        registry = ServiceRegistry(
            service_id="ralfie-api",
            port_range=(7770, 7779),
            mdns_name="ralfie.local",
            metadata={"version": "0.1.0"}
        )

        port = registry.start()

        # In Flask:
        @app.route('/api/health')
        def health():
            return registry.health_response()
    """

    def __init__(
        self,
        service_id: str,
        port_range: Tuple[int, int],
        mdns_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize service registry.

        Args:
            service_id: Unique identifier for this service (e.g., "ralfie-api")
            port_range: Tuple of (min_port, max_port) to search for available port
            mdns_name: Optional mDNS name (e.g., "ralfie.local")
            metadata: Optional metadata to include in health responses
        """
        self.service_id = service_id
        self.port_range = port_range
        self.mdns_name = mdns_name
        self.metadata = metadata or {}
        self.port: Optional[int] = None
        self.start_time: Optional[datetime] = None
        self._zeroconf = None
        self._service_info = None

    def start(self, preferred_port: Optional[int] = None) -> int:
        """
        Find available port and register service.

        Args:
            preferred_port: If specified, try this port first before scanning range

        Returns:
            Port number the service is running on
        """
        # Try preferred port first if specified
        if preferred_port and self._is_port_available(preferred_port):
            self.port = preferred_port
        else:
            self.port = find_available_port(self.port_range)

        self.start_time = datetime.now()

        # Register mDNS if name provided
        if self.mdns_name:
            self._register_mdns()

        return self.port

    def _is_port_available(self, port: int) -> bool:
        """Check if a specific port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return True
        except OSError:
            return False

    def _register_mdns(self):
        """Register mDNS service (requires zeroconf)"""
        try:
            from zeroconf import Zeroconf, ServiceInfo
            import socket as sock

            zeroconf = Zeroconf()

            # Get local IP
            hostname = sock.gethostname()
            local_ip = sock.gethostbyname(hostname)

            # Create service info
            service_type = "_http._tcp.local."
            service_name = f"{self.service_id}.{service_type}"

            info = ServiceInfo(
                service_type,
                service_name,
                addresses=[sock.inet_aton(local_ip)],
                port=self.port,
                properties={
                    'service_id': self.service_id,
                    'version': self.metadata.get('version', '0.0.0'),
                    **self.metadata
                },
                server=f"{self.mdns_name}."
            )

            zeroconf.register_service(info)

            self._zeroconf = zeroconf
            self._service_info = info

            print(f"🌐 mDNS service registered: http://{self.mdns_name}:{self.port}")

        except ImportError:
            print("⚠️  zeroconf not installed, skipping mDNS registration")

    def health_response(self) -> Dict[str, Any]:
        """
        Generate standardized health check response.

        Returns:
            Dict with service health information
        """
        uptime_seconds = None
        if self.start_time:
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        return {
            "service": self.service_id,
            "status": "healthy",
            "port": self.port,
            "mdns": self.mdns_name,
            "uptime_seconds": uptime_seconds,
            "metadata": self.metadata
        }

    def stop(self):
        """Cleanup: unregister mDNS service"""
        if self._zeroconf and self._service_info:
            self._zeroconf.unregister_service(self._service_info)
            self._zeroconf.close()
            print(f"🌐 mDNS service unregistered: {self.mdns_name}")


# Convenience function for simple use cases
def quick_start(
    service_id: str,
    port_range: Tuple[int, int],
    mdns_name: Optional[str] = None
) -> int:
    """
    Quick helper to find and return an available port.

    Args:
        service_id: Service identifier
        port_range: Port range to search
        mdns_name: Optional mDNS name

    Returns:
        Available port number
    """
    registry = ServiceRegistry(service_id, port_range, mdns_name)
    return registry.start()
