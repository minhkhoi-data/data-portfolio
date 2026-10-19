"""Small nbclient compatibility shims for ipykernel's in-process kernel."""
from ipykernel.inprocess.manager import InProcessKernelManager
from ipykernel.inprocess.blocking import BlockingInProcessKernelClient

class CompatInProcessKernelClient(BlockingInProcessKernelClient):
    def wait_for_ready(self, timeout=None):
        # The in-process client is ready as soon as it is constructed; the
        # older method does not accept nbclient's timeout keyword.
        return super().wait_for_ready()

class CompatInProcessKernelManager(InProcessKernelManager):
    client_class='analysis.inprocess_kernel.CompatInProcessKernelClient'

    def shutdown_kernel(self, now=False):
        return super().shutdown_kernel()

    def cleanup_resources(self, restart=False):
        return super().cleanup_resources()
