# PCK File API Documentation

A C# library for reading, modifying, and writing `.pck` archive files.

---

# Overview

The API provides tools for:

* Reading `.pck` files
* Extracting embedded assets
* Modifying asset data and metadata
* Creating new `.pck` archives
* Writing archives back to disk

---

# Architecture

```
PckFile
 ├─ PckAssetCollection
 │   └─ PckAsset
 │       ├─ byte[] Data
 │       └─ PckFileProperties
```

Workflow:

```
.pck file
   ↓
PckFileReader
   ↓
PckFile (in memory)
   ↓
Modify assets
   ↓
PckFileWriter
   ↓
.pck file
```

---

# Namespaces

| Namespace         | Purpose                          |
| ----------------- | -------------------------------- |
| `OMI.Formats.Pck` | Core PCK data structures         |
| `OMI.Workers.Pck` | Reading and writing `.pck` files |
| `OMI`             | Endianness utilities             |
| `OMI.Workers`     | Generic file reader interfaces   |

---

# Core Classes

---

# `PckFile`

Represents a `.pck` archive in memory.

## Constructors

```csharp
PckFile()
```

Creates a file with default type `3`.

```csharp
PckFile(int type)
```

Creates a file with the specified type.

```csharp
PckFile(int type, int xmlVersion)
```

Creates a file with a specific type and XML version.

---

## Fields

```csharp
public readonly int Type
```

Archive type identifier stored in the header.

```csharp
public int xmlVersion
```

Optional XML version metadata.

---

## Properties

```csharp
int AssetCount
```

Number of assets contained in the archive.

---

## Methods

### CreateNewAsset

```csharp
PckAsset CreateNewAsset(string assetName, PckAssetType assetType)
```

Creates a new asset and adds it to the archive.

---

```csharp
PckAsset CreateNewAsset(
    string assetName,
    PckAssetType assetType,
    Func<byte[]> dataInitializer
)
```

Creates a new asset and initializes its data.

Example:

```csharp
var asset = pck.CreateNewAsset(
    "hello.txt",
    PckAssetType.InfoFile,
    () => Encoding.UTF8.GetBytes("hello world")
);
```

---

### GetAsset

```csharp
PckAsset GetAsset(string assetName, PckAssetType assetType)
```

Returns an asset.

Throws `KeyNotFoundException` if the asset does not exist.

---

### TryGetAsset

```csharp
bool TryGetAsset(
    string assetName,
    PckAssetType assetType,
    out PckAsset asset
)
```

Attempts to retrieve an asset safely.

---

### HasAsset

```csharp
bool HasAsset(string assetName, PckAssetType assetType)
```

Checks if an asset exists.

---

### GetOrCreate

```csharp
PckAsset GetOrCreate(string assetName, PckAssetType assetType)
```

Returns an existing asset or creates one.

---

### GetAssets

```csharp
IReadOnlyCollection<PckAsset> GetAssets()
```

Returns all assets in the archive.

---

### GetAssetsByType

```csharp
IEnumerable<PckAsset> GetAssetsByType(PckAssetType type)
```

Returns all assets of a specific type.

---

### RemoveAsset

```csharp
bool RemoveAsset(PckAsset asset)
```

Removes an asset from the archive.

---

### RemoveAll

```csharp
void RemoveAll(Predicate<PckAsset> predicate)
```

Removes all assets matching a condition.

---

### InsertAsset

```csharp
void InsertAsset(int index, PckAsset asset)
```

Inserts an asset at a specific index.

---

# `PckAsset`

Represents a single file stored inside a `.pck` archive.

---

## Constructor

```csharp
PckAsset(string filename, PckAssetType type)
```

---

## Properties

### Filename

```csharp
string Filename
```

Path of the asset inside the archive.

Backslashes are automatically converted to `/`.

Example:

```
textures/blocks/stone.png
```

---

### Type

```csharp
PckAssetType Type
```

Type classification of the asset.

---

### Data

```csharp
byte[] Data
```

Raw binary contents of the asset.

---

### Size

```csharp
int Size
```

Size of the asset in bytes.

---

### PropertyCount

```csharp
int PropertyCount
```

Number of metadata properties attached to the asset.

---

## Methods

### SetData

```csharp
void SetData(byte[] data)
```

Sets the binary contents of the asset.

---

### AddProperty

```csharp
void AddProperty(string name, string value)
```

Adds a metadata property.

---

```csharp
void AddProperty<T>(string name, T value)
```

Generic property version.

---

### RemoveProperty

```csharp
void RemoveProperty(string propertyName)
```

Removes a property.

---

### RemoveProperties

```csharp
void RemoveProperties(string propertyName)
```

Removes all properties with the given key.

---

### HasProperty

```csharp
bool HasProperty(string propertyName)
```

Checks if the property exists.

---

### GetProperty

```csharp
string GetProperty(string propertyName)
```

Returns the property value.

---

### TryGetProperty

```csharp
bool TryGetProperty(string propertyName, out string value)
```

Safe version of property retrieval.

---

### GetProperties

```csharp
IReadOnlyList<KeyValuePair<string,string>> GetProperties()
```

Returns all properties.

---

# `PckAssetType`

Enumeration describing asset categories.

```
SkinFile
CapeFile
TextureFile
UIDataFile
InfoFile
TexturePackInfoFile
LocalisationFile
GameRulesFile
AudioFile
ColourTableFile
GameRulesHeader
SkinDataFile
ModelsFile
BehavioursFile
MaterialFile
```

---

# `PckFileReader`

Reads `.pck` archives.

Namespace:

```
OMI.Workers.Pck
```

---

## Constructors

```csharp
PckFileReader()
```

Uses `BigEndian` byte order.

---

```csharp
PckFileReader(ByteOrder byteOrder)
```

Creates a reader with a specified byte order.

---

## Methods

### FromFile

```csharp
PckFile FromFile(string filename)
```

Reads a `.pck` file from disk.

---

### FromStream

```csharp
PckFile FromStream(Stream stream)
```

Reads a `.pck` archive from a stream.

---

# `PckFileWriter`

Writes `.pck` archives.

Namespace:

```
OMI.Workers.Pck
```

---

## Constructor

```csharp
PckFileWriter(PckFile file, ByteOrder byteOrder)
```

---

## Methods

### WriteToFile

```csharp
void WriteToFile(string filename)
```

Writes the archive to disk.

---

### WriteToStream

```csharp
void WriteToStream(Stream stream)
```

Writes the archive to a stream.

---

# Endianness Utilities

Namespace:

```
OMI
```

---

# `ByteOrder`

Defines byte order.

```
BigEndian
LittleEndian
```

---

# `EndiannessAwareBinaryReader`

A `BinaryReader` that supports endianness-aware reading.

### Methods

```
ReadInt16()
ReadInt32()
ReadInt64()
ReadUInt16()
ReadUInt32()
ReadUInt64()
ReadSingle()
ReadString(int length)
```

---

# `EndiannessAwareBinaryWriter`

A `BinaryWriter` that supports endianness-aware writing.

### Methods

```
Write(short)
Write(int)
Write(long)
Write(float)
WriteString(string)
WriteString(string, int maxLength)
```

---

# Interfaces

Namespace:

```
OMI.Workers
```

---

# `IDataFormatReader`

Generic data reader interface.

```
object FromStream(Stream stream)
object FromFile(string filename)
```

---

# `IDataFormatReader<T>`

Typed reader interface.

```
T FromStream(Stream stream)
T FromFile(string filename)
```

---

# Example Usage

## Reading a `.pck`

```csharp
var reader = new PckFileReader(ByteOrder.BigEndian);
PckFile pck = reader.FromFile("pack.pck");
```

---

## Extracting files

```csharp
foreach (var asset in pck.GetAssets())
{
    File.WriteAllBytes(asset.Filename, asset.Data);
}
```

---

## Modifying an asset

```csharp
var asset = pck.GetAsset(
    "textures/block/stone.png",
    PckAssetType.TextureFile
);

asset.SetData(File.ReadAllBytes("new_stone.png"));
```

---

## Adding a new asset

```csharp
var asset = pck.CreateNewAsset(
    "test.txt",
    PckAssetType.InfoFile
);

asset.SetData(Encoding.UTF8.GetBytes("hello"));
```

---

## Saving the archive

```csharp
var writer = new PckFileWriter(pck, ByteOrder.BigEndian);
writer.WriteToFile("output.pck");
```

---

If you want, Logan, I can also generate a **small developer cheat sheet** for this API (like a **one-page quick reference**) that makes it much faster to remember the most common operations when you're coding.
