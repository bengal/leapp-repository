import os

from leapp.actors import Actor
from leapp.models import InstalledRedHatSignedRPM, InstalledUnsignedRPM, InstalledRPM, RPM
from leapp.tags import IPUWorkflowTag, FactsPhaseTag


class RedHatSignedRpmScanner(Actor):
    name = 'red_hat_signed_rpm_scanner'
    description = 'Scan from installed RPM packages those that were signed or not by Red Hat.'
    consumes = (InstalledRPM,)
    produces = (InstalledRedHatSignedRPM, InstalledUnsignedRPM,)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        RH_SIGS = ['199e2f91fd431d51',
                   '5326810137017186',
                   '938a80caf21541eb',
                   'fd372689897da07a',
                   '45689c882fa658e0']

        signed_pkgs = InstalledRedHatSignedRPM()
        unsigned_pkgs = InstalledUnsignedRPM()

        for rpm_pkgs in self.consume(InstalledRPM):
            for pkg in rpm_pkgs.items:
                if any(key in pkg.pgpsig for key in RH_SIGS):
                    signed_pkgs.items.append(pkg)
                    continue

                unsigned_pkgs.items.append(pkg)

        self.produce(signed_pkgs)
        self.produce(unsigned_pkgs)
