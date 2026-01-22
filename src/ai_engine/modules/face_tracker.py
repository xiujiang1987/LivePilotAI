# -*- coding: utf-8 -*-
"""
LivePilotAI 多人臉追蹤系統
負責在連續幀中跟蹤人臉身份，分配唯一ID
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial import distance as dist
from collections import OrderedDict

logger = logging.getLogger(__name__)

@dataclass
class TrackedFace:
    """被追蹤的人臉"""
    face_id: int
    centroid: Tuple[int, int]
    bbox: Tuple[int, int, int, int] # x, y, w, h
    disappeared_frames: int = 0
    emotion_history: List[str] = None
    
    def __post_init__(self):
        if self.emotion_history is None:
            self.emotion_history = []

class FaceTracker:
    """
    基於質心的人臉追蹤器
    使用歐幾里得距離匹配連續幀中的人臉
    """
    
    def __init__(self, max_disappeared: int = 20, max_distance: int = 100):
        """
        Args:
            max_disappeared: ID被註銷前允許消失的最大幀數
            max_distance: 認定為同一人的最大移動距離 (像素)
        """
        self.next_object_id = 0
        self.objects: Dict[int, TrackedFace] = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        logger.info(f"人臉追蹤器初始化 (Max Disappeared: {max_disappeared})")

    def register(self, centroid: Tuple[int, int], bbox: Tuple[int, int, int, int]):
        """註冊新的人臉ID"""
        self.objects[self.next_object_id] = TrackedFace(
            face_id=self.next_object_id,
            centroid=centroid,
            bbox=bbox
        )
        self.next_object_id += 1

    def deregister(self, object_id: int):
        """註銷人臉ID"""
        del self.objects[object_id]

    def update(self, rects: List[Tuple[int, int, int, int]]) -> Dict[int, TrackedFace]:
        """
        更新追蹤狀態
        
        Args:
           rects: 當前幀檢測到的人臉邊框列表 [(x, y, w, h), ...]
           
        Returns:
            當前活動的追蹤對象字典 {id: TrackedFace}
        """
        if len(rects) == 0:
            # 如果沒有檢測到人臉，增加所有現有對象的消失計數
            for object_id in list(self.objects.keys()):
                self.objects[object_id].disappeared_frames += 1
                if self.objects[object_id].disappeared_frames > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        # 計算當前幀所有人臉的質心
        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (x, y, w, h)) in enumerate(rects):
            cX = int(x + w / 2.0)
            cY = int(y + h / 2.0)
            input_centroids[i] = (cX, cY)

        # 如果當前沒有追蹤對象，全部註冊
        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(tuple(input_centroids[i]), rects[i])
        else:
            # 嘗試匹配現有對象
            object_ids = list(self.objects.keys())
            object_centroids = [obj.centroid for obj in self.objects.values()]
            
            # 計算距離矩陣
            D = dist.cdist(np.array(object_centroids), input_centroids)
            
            # 找出最小距離的索引
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                    
                # 如果距離過大，不認為是同一人
                if D[row, col] > self.max_distance:
                    continue
                    
                object_id = object_ids[row]
                self.objects[object_id].centroid = tuple(input_centroids[col])
                self.objects[object_id].bbox = rects[col]
                self.objects[object_id].disappeared_frames = 0
                
                used_rows.add(row)
                used_cols.add(col)
                
            # 處理未匹配的現有對象 (消失)
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            for row in unused_rows:
                object_id = object_ids[row]
                self.objects[object_id].disappeared_frames += 1
                if self.objects[object_id].disappeared_frames > self.max_disappeared:
                    self.deregister(object_id)
                    
            # 處理未匹配的新輸入 (新出現)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            for col in unused_cols:
                self.register(tuple(input_centroids[col]), rects[col])

        return self.objects
