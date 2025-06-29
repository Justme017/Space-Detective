#!/usr/bin/env python3
"""Test script for image URLs"""

from wiki_utils import get_object_image_url

print("Testing image URL functionality:")
test_objects = ['Moon', 'Mars', 'Mercury', 'Venus', 'Jupiter', 'Saturn']

for obj in test_objects:
    url = get_object_image_url(obj)
    print(f"{obj}: {url}")

print("Test completed!")
