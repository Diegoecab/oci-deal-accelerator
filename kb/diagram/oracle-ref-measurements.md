# Oracle Architecture Center Reference Diagram Measurements

Extracted from official Oracle .drawio source files (draw.io/28.0.4, Visio-exported).

Sources analyzed:
1. Hub-and-Spoke DRG (hub-spoke-network-drg) - single-region, 3 VCNs, hub topology
2. Essbase Cross-Region DR (cross-region-dr-essbase-oci) - dual-region, 3 ADs each, DR topology

Tool: draw.io 28.0.4 (Electron), exported from Visio (.vsdx)

---

## 1. Canvas / Page Settings

| Property | Hub-Spoke DRG | Essbase DR |
|----------|--------------|------------|
| pageWidth | 850 | 850 |
| pageHeight | 1100 | 1100 |
| gridSize | 10 | 10 |
| Actual content W | 693 | 2339 |
| Actual content H | 846 | 1154 |

---

## 2. Font Specifications

| Usage | Font Family | Font Size | Style |
|-------|------------|-----------|-------|
| Region/VCN/service labels | Oracle Sans | 16.93px (~17px) | Bold for region title |
| Annotation text | Oracle Sans | 14.82px (~15px) | Regular |
| Label box height | - | 20px | - |
| Annotation box height | - | 17px | - |

---

## 3. Color Palette

| Element | Hex |
|---------|-----|
| OCI Region fill | #f5f4f2 |
| OCI Region stroke | #9e9892 |
| VCN / Subnet border (dashed) | #aa643b |
| Connector lines / solid borders | #312d2a |
| Service icon primary (teal) | #2d5967 |
| Connector lines (Essbase) | #161513 |
| AD fill (multi-AD diagrams) | #e4e1dd |
| Background | #FFFFFF |
| Accent brown | #ae562c |

---

## 4. Container Dimensions

### 4.1 OCI Region
- Hub-Spoke: 456x845 at (236,0), fill=#f5f4f2, stroke=#9e9892
- Essbase Left: 995x849 at (0,305)
- Essbase Right: 1080x849 at (1258,304)
- Pattern: Double-rendered (fill layer + stroke layer as separate shapes)

### 4.2 VCN
- DMZ VCN (Hub-Spoke): 226x354 at (456,26)
- Spoke VCN 1: 226x205 at (456,406)
- Spoke VCN 2: 226x202 at (457,634)
- Essbase left VCN: 894x766 at (30,355)
- Essbase right VCN: 872x766 at (1328,354)
- Style: strokeColor=#aa643b, strokeWidth=2, dashed=1, dashPattern=4.00 2.00

### 4.3 Subnet
- Management Subnet: 176x134 at (498,76)
- Services Subnet: 176x134 at (498,238)
- Workload Subnet 1: 175x143 at (500,458)
- Workload Subnet 2: 175x142 at (500,686)
- Style: Same as VCN (strokeColor=#aa643b, strokeWidth=2, dashed)

### 4.4 Availability Domain (Essbase)
- Width: 188, Height: 815
- Positions: x=211, 425, 632 (left region), x=1508, 1724, 1930 (right region)
- AD-to-AD gap: 18-28px (~25px avg)
- Style: fill=#e4e1dd, stroke=#9e9892

### 4.5 On-Premises Box (Essbase)
- 260x251 at (997,0) - centered between two regions
- Style: fill=#f5f4f2, stroke=#9e9892

### 4.6 Workload Rows (Essbase)
- Standard row: 807x111
- Bottom row (expanded): 807x149
- Y positions: 415, 552, 690, 828, 962
- Row-to-row gap: 23-27px (~25px)

### 4.7 Compartment Boxes (Essbase)
- 189x49 - placed at AD/row intersections

---

## 5. Icon Dimensions

### 5.1 Service Icons (VM, Bastion, Database, etc.)
- 3-layer nesting: 63x63 outer > 61x61 middle > 60x60 inner
- Standard service icon = 60px rendered in 63px box
- Internal details: 13x13 grid cells, 43x13 bottom bar, 3x3 dots

### 5.2 Gateway Icons (IGW, NAT, SGW, DRG attachments)
- 3-layer nesting: 42x42 outer > 41x41 middle > 40x40 inner
- Central symbol: 29x26, internal detail: 22x29
- Status indicators: 4x4 dots, 5x1 bars

### 5.3 OCI Toolkit Icons (Bastion-type)
- 40x63 outer > 39x61 middle > 34x58 inner (portrait orientation)

### 5.4 Database/Storage Icons
- 59x63 outer > 58x61 middle > inner symbol 39x26 + 21x21

### 5.5 External Icons (Internet, On-Premises)
- Same 63x63 as service icons

---

## 6. Spacing Rules

### 6.1 Vertical Spacing
| Measurement | Value |
|-------------|-------|
| Region label Y offset | 7px from region top |
| VCN/Subnet label Y offset | 8px from container top |
| VCN top to first subnet | 50px |
| Subnet-to-subnet gap | 28px |
| VCN-to-VCN gap | 26px |
| Workload row gap | 23-27px (~25px) |
| Gateway Y within VCN | 29px from VCN top |

### 6.2 Horizontal Spacing
| Measurement | Value |
|-------------|-------|
| VCN to subnet left indent | 42-44px |
| Service icon X within subnet | 80px from subnet left |
| Gateway X from VCN left | 168px |
| AD-to-AD gap | 18-28px (~25px) |
| Inter-region gap (Essbase) | 263px |

### 6.3 Label Spacing
| Measurement | Value |
|-------------|-------|
| Label box height | 20px (standard) |
| Annotation box height | 17px |
| Line-to-line spacing | 17px |

---

## 7. Connector Styles

Oracle Visio-exported .drawio files do NOT use draw.io native edges. Connectors are thin rectangles:
- Horizontal: Wx1 rectangles, stroke=#312d2a
- Vertical: 2xH or 1xH rectangles
- Cross-region (Essbase): stroke=#161513
- Examples:
  - Internet-to-Gateway: 350x1 at (80,153)
  - Mid-connections: 156x1 at (98,524)
  - DR replication: 549x1 at (391,1045)
  - Vertical link: 1x65 at (1128,365)

---

## 8. Border/Stroke Styles

| Element | strokeColor | strokeWidth | dashed | dashPattern |
|---------|------------|-------------|--------|-------------|
| Region | #9e9892 | 1 | No | - |
| VCN | #aa643b | 2 | Yes | 4.00 2.00 |
| Subnet | #aa643b | 2 | Yes | 4.00 2.00 |
| AD | #9e9892 | 1 | No | - |
| Solid grouping | #312d2a | 2 | No | - |
| Connector | #312d2a/#161513 | 1 | No | - |

---

## 9. Double-Layer Container Rendering

Oracle renders each container as TWO overlapping shapes:
1. Fill layer: fillColor=<color>, strokeColor=none
2. Stroke layer: fillColor=none, strokeColor=<color>

This pattern applies to Region, VCN, Subnet, and AD containers.

---

## 10. Key Proportional Ratios

| Ratio | Value | Description |
|-------|-------|-------------|
| Gateway:Service icon | 42:63 = 0.67 | Gateways 2/3 size of service icons |
| VCN:Subnet width | 226:176 = 1.28 | VCN ~28% wider than subnet |
| VCN left padding | 42-44px | Subnet indent |
| VCN top padding | 50px | To first subnet |
| VCN bottom padding | ~22-26px | After last subnet |
| Region aspect (hub-spoke) | 456:845 = 0.54 | Portrait |
| AD aspect (multi-AD) | 188:815 = 0.23 | Very tall/narrow |
| Workload row aspect | 807:111 = 7.27 | Very wide/short |

---

## 11. Recommended Calibration for oci_diagram_gen.py

```yaml
region:
  min_width: 456
  min_height: 845
  fill: "#f5f4f2"
  stroke: "#9e9892"
  stroke_width: 1
  corner_radius: 0

vcn:
  min_width: 226
  typical_height_hub: 205
  typical_height_dmz: 354
  stroke: "#aa643b"
  stroke_width: 2
  dashed: true
  dash_pattern: "4 2"

subnet:
  width: 176
  typical_height: 134-143
  stroke: "#aa643b"
  stroke_width: 2
  dashed: true
  dash_pattern: "4 2"

availability_domain:
  width: 188
  height: 815
  fill: "#e4e1dd"
  stroke: "#9e9892"

service_icon:
  outer: 63
  rendered: 60

gateway_icon:
  outer: 42
  rendered: 40
  inner_symbol: 29x26

spacing:
  vcn_to_vcn_gap: 26
  subnet_to_subnet_gap: 28
  vcn_top_to_first_subnet: 50
  vcn_left_to_subnet: 42
  subnet_to_service_icon: 80
  gateway_x_from_vcn_left: 168
  gateway_y_from_vcn_top: 29
  label_y_offset: 8
  region_label_y: 7
  workload_row_gap: 25
  ad_to_ad_gap: 25
  inter_region_gap: 263

fonts:
  family: "Oracle Sans"
  label_size: 17
  annotation_size: 15
  label_box_height: 20
  annotation_box_height: 17

colors:
  region_fill: "#f5f4f2"
  region_stroke: "#9e9892"
  vcn_stroke: "#aa643b"
  subnet_stroke: "#aa643b"
  ad_fill: "#e4e1dd"
  icon_primary: "#2d5967"
  text_dark: "#312d2a"
  connector: "#312d2a"
  background: "#FFFFFF"
```

---

## 12. Layout Patterns

### Single-Region Hub-Spoke
- VCNs stacked vertically
- External icons (Internet, On-Prem) at far left
- Gateways between external and VCN
- DRG centered with route table
- Service icons right-aligned within subnets

### Dual-Region DR
- Regions side by side horizontally
- On-Premises box centered above/between regions
- ADs as vertical columns within each region
- Workload tiers as horizontal rows crossing all ADs
- Compartment boxes at AD-row intersections
- DR arrows as horizontal lines between matching rows
