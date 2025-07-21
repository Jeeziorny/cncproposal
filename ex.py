#!/usr/bin/env python3
"""
Example: Separated vs Unified Geometry Approaches
Demonstrates how code extends in both patterns
"""

import math
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# APPROACH 1: SEPARATED STRUCTURES (Current approach)
# =============================================================================

@dataclass
class Point:
    x: float
    y: float

class ValidationError:
    def __init__(self, code: str, message: str, position: Point = None):
        self.code = code
        self.message = message
        self.position = position

class GeometryBase(ABC):
    def __init__(self, id: str, layer: str = "0"):
        self.id = id
        self.layer = layer
    
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass
    
    @abstractmethod
    def validate(self) -> List[ValidationError]:
        pass
    
    @abstractmethod
    def to_gcode_segments(self, precision: float = 0.1) -> List[str]:
        pass
    
    @abstractmethod
    def get_bounds(self) -> Dict[str, float]:
        pass

class Circle(GeometryBase):
    def __init__(self, id: str, center: Point, radius: float, layer: str = "0"):
        super().__init__(id, layer)
        self.center = center
        self.radius = radius
        self.type = "circle"
    
    def area(self) -> float:
        return math.pi * self.radius ** 2
    
    def perimeter(self) -> float:
        return 2 * math.pi * self.radius
    
    def validate(self) -> List[ValidationError]:
        errors = []
        if self.radius <= 0:
            errors.append(ValidationError("INVALID_GEOMETRY", 
                                        f"Circle {self.id} has invalid radius: {self.radius}",
                                        self.center))
        if self.radius < 0.5:  # Manufacturing constraint
            errors.append(ValidationError("MANUFACTURING_WARNING", 
                                        f"Circle {self.id} radius {self.radius}mm may be too small for blade",
                                        self.center))
        return errors
    
    def to_gcode_segments(self, precision: float = 0.1) -> List[str]:
        """Generate G-code for circle cutting"""
        segments = []
        # Move to start position
        start_x = self.center.x + self.radius
        segments.append(f"G0 X{start_x:.3f} Y{self.center.y:.3f}")
        
        # Full circle with G02 (clockwise)
        segments.append(f"G02 X{start_x:.3f} Y{self.center.y:.3f} I{-self.radius:.3f} J0")
        return segments
    
    def get_bounds(self) -> Dict[str, float]:
        return {
            "minX": self.center.x - self.radius,
            "maxX": self.center.x + self.radius,
            "minY": self.center.y - self.radius,
            "maxY": self.center.y + self.radius
        }

class Line(GeometryBase):
    def __init__(self, id: str, start_point: Point, end_point: Point, layer: str = "0"):
        super().__init__(id, layer)
        self.start_point = start_point
        self.end_point = end_point
        self.type = "line"
    
    def area(self) -> float:
        return 0.0  # Lines have no area
    
    def perimeter(self) -> float:
        return self.length()
    
    def length(self) -> float:
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y
        return math.sqrt(dx**2 + dy**2)
    
    def validate(self) -> List[ValidationError]:
        errors = []
        if self.start_point.x == self.end_point.x and self.start_point.y == self.end_point.y:
            errors.append(ValidationError("REDUNDANT_POINTS", 
                                        f"Line {self.id} has identical start and end points",
                                        self.start_point))
        
        length = self.length()
        if length < 0.001:  # Too short for manufacturing
            errors.append(ValidationError("REDUNDANT_POINTS", 
                                        f"Line {self.id} length {length:.6f}mm too short",
                                        self.start_point))
        return errors
    
    def to_gcode_segments(self, precision: float = 0.1) -> List[str]:
        """Generate G-code for line cutting"""
        return [f"G01 X{self.end_point.x:.3f} Y{self.end_point.y:.3f}"]
    
    def get_bounds(self) -> Dict[str, float]:
        return {
            "minX": min(self.start_point.x, self.end_point.x),
            "maxX": max(self.start_point.x, self.end_point.x),
            "minY": min(self.start_point.y, self.end_point.y),
            "maxY": max(self.start_point.y, self.end_point.y)
        }


# =============================================================================
# EXTENDING SEPARATED APPROACH: Adding Arc class
# =============================================================================

class Arc(GeometryBase):
    def __init__(self, id: str, center: Point, radius: float, start_angle: float, end_angle: float, layer: str = "0"):
        super().__init__(id, layer)
        self.center = center
        self.radius = radius
        self.start_angle = start_angle  # degrees
        self.end_angle = end_angle      # degrees
        self.type = "arc"
    
    def area(self) -> float:
        return 0.0  # Arcs have no area (they're curves)
    
    def perimeter(self) -> float:
        angle_span = abs(self.end_angle - self.start_angle)
        return (angle_span / 360.0) * 2 * math.pi * self.radius
    
    def validate(self) -> List[ValidationError]:
        errors = []
        if self.radius <= 0:
            errors.append(ValidationError("INVALID_GEOMETRY", 
                                        f"Arc {self.id} has invalid radius: {self.radius}",
                                        self.center))
        
        angle_span = abs(self.end_angle - self.start_angle)
        if angle_span < 0.1:
            errors.append(ValidationError("REDUNDANT_POINTS", 
                                        f"Arc {self.id} has negligible sweep angle: {angle_span}°",
                                        self.center))
        
        # Arc-specific: detect if it should be a circle
        if abs(angle_span - 360) < 0.001:
            errors.append(ValidationError("REDUNDANT_POINTS", 
                                        f"Arc {self.id} sweeps 360° - consider using Circle instead",
                                        self.center))
        return errors
    
    def to_gcode_segments(self, precision: float = 0.1) -> List[str]:
        """Generate G-code for arc cutting"""
        # Calculate start and end points
        start_rad = math.radians(self.start_angle)
        end_rad = math.radians(self.end_angle)
        
        start_x = self.center.x + self.radius * math.cos(start_rad)
        start_y = self.center.y + self.radius * math.sin(start_rad)
        end_x = self.center.x + self.radius * math.cos(end_rad)
        end_y = self.center.y + self.radius * math.sin(end_rad)
        
        # Move to start
        segments = [f"G0 X{start_x:.3f} Y{start_y:.3f}"]
        
        # Arc interpolation (G02 for clockwise, G03 for counterclockwise)
        direction = "G02" if self.end_angle > self.start_angle else "G03"
        i_offset = self.center.x - start_x
        j_offset = self.center.y - start_y
        
        segments.append(f"{direction} X{end_x:.3f} Y{end_y:.3f} I{i_offset:.3f} J{j_offset:.3f}")
        return segments
    
    def get_bounds(self) -> Dict[str, float]:
        # For simplicity, return bounding box of full circle
        # Real implementation would calculate actual arc bounds
        return {
            "minX": self.center.x - self.radius,
            "maxX": self.center.x + self.radius,
            "minY": self.center.y - self.radius,
            "maxY": self.center.y + self.radius
        }


# =============================================================================
# APPROACH 2: UNIFIED STRUCTURE (Your proposed approach)
# =============================================================================

class GeometryType(Enum):
    LINE = "line"
    ARC = "arc"
    CIRCLE = "circle"

class UnifiedGeometry:
    def __init__(self, id: str, point_a: Point, point_b: Point, point_c: Point = None, angle: float = 0, layer: str = "0"):
        self.id = id
        self.point_a = point_a  # Start point
        self.point_b = point_b  # End point
        self.point_c = point_c  # Control point for arcs
        self.angle = angle      # Curve amount
        self.layer = layer
        
        # Auto-detect type
        self.geometry_type = self._detect_type()
    
    def _detect_type(self) -> GeometryType:
        """Detect geometry type from points and angle"""
        if self.point_a.x == self.point_b.x and self.point_a.y == self.point_b.y:
            return GeometryType.CIRCLE
        elif self.angle == 0 or self.point_c is None:
            return GeometryType.LINE
        else:
            return GeometryType.ARC
    
    def area(self) -> float:
        if self.geometry_type == GeometryType.CIRCLE:
            radius = self._calculate_circle_radius()
            return math.pi * radius ** 2
        else:
            return 0.0  # Lines and arcs have no area
    
    def perimeter(self) -> float:
        if self.geometry_type == GeometryType.LINE:
            return self._calculate_line_length()
        elif self.geometry_type == GeometryType.CIRCLE:
            radius = self._calculate_circle_radius()
            return 2 * math.pi * radius
        else:  # ARC
            return self._calculate_arc_length()
    
    def _calculate_line_length(self) -> float:
        dx = self.point_b.x - self.point_a.x
        dy = self.point_b.y - self.point_a.y
        return math.sqrt(dx**2 + dy**2)
    
    def _calculate_circle_radius(self) -> float:
        # For circles, point_c could represent center, or derive from angle
        if self.point_c:
            dx = self.point_c.x - self.point_a.x
            dy = self.point_c.y - self.point_a.y
            return math.sqrt(dx**2 + dy**2)
        else:
            # Derive from angle or other method - this gets complex!
            return abs(self.angle)  # Simplified assumption
    
    def _calculate_arc_length(self) -> float:
        # Complex calculation requiring arc reconstruction
        # This is where the unified approach becomes difficult
        if self.point_c:
            # Calculate radius and sweep angle from three points
            center, radius, start_angle, end_angle = self._reconstruct_arc()
            angle_span = abs(end_angle - start_angle)
            return (angle_span / 360.0) * 2 * math.pi * radius
        else:
            return self._calculate_line_length()  # Fallback
    
    def _reconstruct_arc(self):
        """Complex calculation to reconstruct arc from three points"""
        # This is mathematically intensive and error-prone
        # Placeholder implementation
        center = Point((self.point_a.x + self.point_b.x) / 2, 
                      (self.point_a.y + self.point_b.y) / 2)
        radius = self._calculate_line_length() / 2
        start_angle = 0
        end_angle = self.angle
        return center, radius, start_angle, end_angle
    
    def validate(self) -> List[ValidationError]:
        """Validation becomes complex - need to detect type first"""
        errors = []
        
        if self.geometry_type == GeometryType.LINE:
            # Line validation
            if self.point_a.x == self.point_b.x and self.point_a.y == self.point_b.y:
                errors.append(ValidationError("REDUNDANT_POINTS", 
                                            f"Geometry {self.id} has identical start and end points",
                                            self.point_a))
            
            length = self._calculate_line_length()
            if length < 0.001:
                errors.append(ValidationError("REDUNDANT_POINTS", 
                                            f"Geometry {self.id} length too short: {length:.6f}mm",
                                            self.point_a))
        
        elif self.geometry_type == GeometryType.CIRCLE:
            # Circle validation
            radius = self._calculate_circle_radius()
            if radius <= 0:
                errors.append(ValidationError("INVALID_GEOMETRY", 
                                            f"Geometry {self.id} has invalid radius: {radius}",
                                            self.point_a))
        
        elif self.geometry_type == GeometryType.ARC:
            # Arc validation - requires reconstruction
            try:
                center, radius, start_angle, end_angle = self._reconstruct_arc()
                if radius <= 0:
                    errors.append(ValidationError("INVALID_GEOMETRY", 
                                                f"Geometry {self.id} has invalid arc radius: {radius}",
                                                center))
                
                angle_span = abs(end_angle - start_angle)
                if abs(angle_span - 360) < 0.001:
                    errors.append(ValidationError("REDUNDANT_POINTS", 
                                                f"Geometry {self.id} sweeps 360° - should be circle",
                                                center))
            except Exception as e:
                errors.append(ValidationError("INVALID_GEOMETRY", 
                                            f"Geometry {self.id} arc reconstruction failed: {str(e)}",
                                            self.point_a))
        
        return errors
    
    def to_gcode_segments(self, precision: float = 0.1) -> List[str]:
        """G-code generation requires type detection and complex logic"""
        if self.geometry_type == GeometryType.LINE:
            return [f"G01 X{self.point_b.x:.3f} Y{self.point_b.y:.3f}"]
        
        elif self.geometry_type == GeometryType.CIRCLE:
            # Circle G-code - need to calculate center and radius
            radius = self._calculate_circle_radius()
            center = self.point_c if self.point_c else Point(self.point_a.x, self.point_a.y)
            start_x = center.x + radius
            
            return [
                f"G0 X{start_x:.3f} Y{center.y:.3f}",
                f"G02 X{start_x:.3f} Y{center.y:.3f} I{-radius:.3f} J0"
            ]
        
        else:  # ARC
            # Arc G-code - complex reconstruction needed
            try:
                center, radius, start_angle, end_angle = self._reconstruct_arc()
                start_rad = math.radians(start_angle)
                end_rad = math.radians(end_angle)
                
                start_x = center.x + radius * math.cos(start_rad)
                start_y = center.y + radius * math.sin(start_rad)
                end_x = center.x + radius * math.cos(end_rad)
                end_y = center.y + radius * math.sin(end_rad)
                
                direction = "G02" if end_angle > start_angle else "G03"
                i_offset = center.x - start_x
                j_offset = center.y - start_y
                
                return [
                    f"G0 X{start_x:.3f} Y{start_y:.3f}",
                    f"{direction} X{end_x:.3f} Y{end_y:.3f} I{i_offset:.3f} J{j_offset:.3f}"
                ]
            except:
                # Fallback to line
                return [f"G01 X{self.point_b.x:.3f} Y{self.point_b.y:.3f}"]
    
    def get_bounds(self) -> Dict[str, float]:
        """Bounds calculation requires type-specific logic"""
        if self.geometry_type == GeometryType.LINE:
            return {
                "minX": min(self.point_a.x, self.point_b.x),
                "maxX": max(self.point_a.x, self.point_b.x),
                "minY": min(self.point_a.y, self.point_b.y),
                "maxY": max(self.point_a.y, self.point_b.y)
            }
        elif self.geometry_type == GeometryType.CIRCLE:
            radius = self._calculate_circle_radius()
            center = self.point_c if self.point_c else Point(self.point_a.x, self.point_a.y)
            return {
                "minX": center.x - radius,
                "maxX": center.x + radius,
                "minY": center.y - radius,
                "maxY": center.y + radius
            }
        else:  # ARC - simplified to full circle bounds
            try:
                center, radius, _, _ = self._reconstruct_arc()
                return {
                    "minX": center.x - radius,
                    "maxX": center.x + radius,
                    "minY": center.y - radius,
                    "maxY": center.y + radius
                }
            except:
                return self.get_bounds()  # Fallback to line bounds


# Separated approach: Clean extension via inheritance/mixins
class CNCOptimizedGeometry(GeometryBase):
    @abstractmethod
    def suggest_blade_rotations(self, blade_diameter: float) -> List[Dict[str, Any]]:
        pass

class CNCOptimizedCircle(Circle, CNCOptimizedGeometry):
    def suggest_blade_rotations(self, blade_diameter: float) -> List[Dict[str, Any]]:
        """Circle-specific blade rotation optimization"""
        rotations = []
        circumference = self.perimeter()
        optimal_segments = max(4, int(circumference / (blade_diameter * 3)))
        
        for i in range(optimal_segments):
            angle = (360 / optimal_segments) * i
            angle_rad = math.radians(angle)
            position = Point(
                self.center.x + self.radius * math.cos(angle_rad),
                self.center.y + self.radius * math.sin(angle_rad)
            )
            rotations.append({
                "position": position,
                "angle": angle + 90,  # Tangent to circle
                "reason": "optimal_circle_segment"
            })
        
        return rotations

class CNCOptimizedLine(Line, CNCOptimizedGeometry):
    def suggest_blade_rotations(self, blade_diameter: float) -> List[Dict[str, Any]]:
        """Line-specific blade rotation optimization"""
        # Lines typically need rotation only at direction changes
        # This would be calculated based on adjacent geometries
        return []  # Simplified for demo

# Unified approach: Complex conditional logic needed
class CNCOptimizedUnifiedGeometry(UnifiedGeometry):
    def suggest_blade_rotations(self, blade_diameter: float) -> List[Dict[str, Any]]:
        """Blade rotation for unified geometry - complex branching"""
        if self.geometry_type == GeometryType.CIRCLE:
            # Duplicate circle logic from separated approach
            radius = self._calculate_circle_radius()
            circumference = 2 * math.pi * radius
            optimal_segments = max(4, int(circumference / (blade_diameter * 3)))
            
            rotations = []
            center = self.point_c if self.point_c else Point(self.point_a.x, self.point_a.y)
            
            for i in range(optimal_segments):
                angle = (360 / optimal_segments) * i
                angle_rad = math.radians(angle)
                position = Point(
                    center.x + radius * math.cos(angle_rad),
                    center.y + radius * math.sin(angle_rad)
                )
                rotations.append({
                    "position": position,
                    "angle": angle + 90,
                    "reason": "optimal_circle_segment"
                })
            
            return rotations
        
        elif self.geometry_type == GeometryType.LINE:
            # Duplicate line logic
            return []
        
        elif self.geometry_type == GeometryType.ARC:
            # Complex arc logic requiring reconstruction
            try:
                center, radius, start_angle, end_angle = self._reconstruct_arc()
                # Arc-specific optimization logic here...
                return []
            except:
                return []
        
        return []
