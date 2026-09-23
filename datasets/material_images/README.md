# Circular Economy Material Image Dataset
**DEVELOPMENT & BENCHMARK DIRECTORY**

This directory defines the circular waste material classification taxonomy.
Supported categories:
- 0: Plastic (PET, HDPE, LDPE, PP bottles and polymers)
- 1: Aluminum (Cans, extruded profiles, cast alloys)
- 2: Copper (Wires, cabling, copper pipe scrap)
- 3: Steel (Structural beams, sheet metal, scrap rods)
- 4: Paper (Office paper, newspapers, pulp)
- 5: Glass (Bottles, cullet, float glass)
- 6: Textile (Cotton remnants, garment cuttings, synthetic yarn)
- 7: E-waste (Printed circuit boards, motherboards, IC components)
- 8: Cardboard (Corrugated boxes, packaging cartons)
- 9: Other (Mixed composite circular waste)

The vision inference pipeline uses MobileNetV2 transfer learning with fallback heuristic feature classification when operating in rapid local development environments.
