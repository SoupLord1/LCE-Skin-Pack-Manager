import clr
import sys

clr.AddReference("OMI-Filetypes")

from OMI.Workers.Pck import PckFileReader
from OMI import ByteOrder

reader = PckFileReader(ByteOrder.LittleEndian)
pck = reader.FromFile("GroupPack.pck")

print
print("pck:")
print(dir(pck))
print()
print("asset:")
print(pck.Type)
for asset in pck.GetAssets():
    print(dir(asset.Value))
    break


def add_skin(filename : str, displayname: str):
    pass