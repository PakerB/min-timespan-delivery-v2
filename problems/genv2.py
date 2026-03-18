import random
import math
import os

class InstanceGenerator:
    def __init__(
        self,
        num_customers=20,
        num_trucks=1,
        num_drones=0,
        map_size=35000.0,
        drone_endurance=700.0,
        drone_speed=31.2928,
        truck_speed=15.6464,
        p_near=0.5,
        p_light_near=0.80,
        p_light_far=0.50,
        min_demand=0.1,
        light_max_demand=1.25,
        heavy_max_demand=49.0,
        seed=None,
    ):
        self.num_customers = num_customers
        self.num_trucks = num_trucks
        self.num_drones = num_drones
        self.map_size = map_size
        self.drone_endurance = drone_endurance
        self.drone_speed = drone_speed
        self.truck_speed = truck_speed
        self.p_near = p_near
        self.p_light_near = p_light_near
        self.p_light_far = p_light_far
        self.min_demand = min_demand
        self.light_max_demand = light_max_demand
        self.heavy_max_demand = heavy_max_demand
        
        if seed is not None:
            random.seed(seed)
        
        self.drone_radius_m = (self.drone_endurance / 2.0) * self.drone_speed
    
    def _distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def _sample_location_near(self, depot_x, depot_y):
        while True:
            rho = self.drone_radius_m * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()
            x = depot_x + rho * math.cos(theta)
            y = depot_y + rho * math.sin(theta)
            half_size = self.map_size / 2.0
            if -half_size <= x <= half_size and -half_size <= y <= half_size:
                return x, y
    
    def _sample_location_far(self):
        half_size = self.map_size / 2.0
        x = random.uniform(-half_size, half_size)
        y = random.uniform(-half_size, half_size)
        return x, y
    
    def _sample_demand(self, x, y, depot_x, depot_y):
        dist = self._distance(x, y, depot_x, depot_y)
        is_near = dist <= self.drone_radius_m
        if is_near:
            if random.random() < self.p_light_near:
                demand = random.uniform(self.min_demand, self.light_max_demand)
            else:
                demand = random.uniform(self.light_max_demand, self.heavy_max_demand)
        else:
            if random.random() < self.p_light_far:
                demand = random.uniform(self.min_demand, self.light_max_demand)
            else:
                demand = random.uniform(self.light_max_demand, self.heavy_max_demand)
        return demand
    
    def generate(self):
        depot_x, depot_y = 0.0, 0.0
        customers = []
        for i in range(self.num_customers):
            if random.random() < self.p_near:
                x, y = self._sample_location_near(depot_x, depot_y)
            else:
                x, y = self._sample_location_far()
            demand = self._sample_demand(x, y, depot_x, depot_y)
            customers.append({'x': x, 'y': y, 'dronable': 1, 'demand': demand})
        return {'depot': (depot_x, depot_y), 'customers': customers}
    
    def save_to_file(self, instance, filename):
        # GIỮ NGUYÊN FORMAT FILE CŨ THEO YÊU CẦU
        with open(filename, 'w') as f:
            f.write(f"trucks_count {self.num_trucks}\n")
            f.write(f"drones_count {self.num_drones}\n")
            f.write(f"customers {self.num_customers}\n")
            f.write(f"depot {instance['depot'][0]} {instance['depot'][1]}\n")
            f.write(f"{'Coordinate X':<20} {'Coordinate Y':<20} Dronable Demand\n")
            for customer in instance['customers']:
                f.write(f"{customer['x']:<20} {customer['y']:<20} {customer['dronable']:<9} {customer['demand']}\n")

def main():
    # ============================================================
    # CẤU HÌNH TỰ ĐỘNG
    # ============================================================
    total_instances = 4000        # Tổng số file mục tiêu
    customer_steps = range(20, 110, 10)  # [20, 30, ..., 100]
    instances_per_step = total_instances // len(customer_steps)
    
    output_dir = os.path.join("problems", "data")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Đang sinh {total_instances} file vào thư mục: {output_dir}")

    for num_customers in customer_steps:
        # 1. Tự động điều chỉnh Map Size theo số khách
        # Ví dụ: 20 khách -> 18km, 100 khách -> 50km
        map_size = 10000.0 + (num_customers * 400.0)
        map_km = int(map_size / 1000)
        
        # 2. Tự động tính số lượng xe
        num_trucks = max(1, num_customers // 20)
        num_drones = num_trucks * 2
        
        generator = InstanceGenerator(
            num_customers=num_customers,
            num_trucks=num_trucks,
            num_drones=num_drones,
            map_size=map_size,
            drone_endurance=700.0,
        )

        print(f"-> Kịch bản {num_customers} khách: Map {map_km}km, {num_trucks} Truck, {num_drones} Drone")
        
        # 3. Sinh các instance cho kịch bản này
        # Tên file: {khách}.{map}.{số_thứ_tự}.txt (để tránh trùng lặp trong 1 folder)
        for i in range(1, instances_per_step + 1):
            filename = f"{num_customers}.{map_km}.{i}.txt"
            filepath = os.path.join(output_dir, filename)
            
            instance = generator.generate()
            generator.save_to_file(instance, filepath)
            
            if i % 500 == 0:
                print(f"   Đã xong {i}/{instances_per_step} file...")

    print(f"\nHOÀN TẤT! Tất cả file đã được lưu tại: {output_dir}")

if __name__ == '__main__':
    main()