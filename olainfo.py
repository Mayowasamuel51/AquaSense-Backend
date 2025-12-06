import 'package:aquasense/models/unitmodel.dart';

// ======================
// Batch Model
// ======================

class BatchModel {
  final String batchId;
  final int farmerId;
  final String batchName;
  final String fishtype;
  final List<UnitRecordModel>? records;
  final int isCompleted;
  final int numberoffishes;
  final int ageAtStock;
  final double averagebodyweight;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  BatchModel({
    required this.batchId,
    required this.farmerId,
    required this.batchName,
    required this.fishtype,
    required this.numberoffishes,
    required this.averagebodyweight,
    required this.ageAtStock,
    this.records,
    this.isCompleted = 0,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  BatchModel copyWith({
    List<UnitRecordModel>? records,
    int? isCompleted,
    int? numberoffishes,
    int? ageAtStock,
    double? averagebodyweight,
    int? isSynced,
    DateTime? updatedAt,
  }) {
    return BatchModel(
      batchId: batchId,
      farmerId: farmerId,
      batchName: batchName,
      fishtype: fishtype,
      records: records ?? this.records,
      averagebodyweight: averagebodyweight ?? this.averagebodyweight,
      isCompleted: isCompleted ?? this.isCompleted,
      numberoffishes: numberoffishes ?? this.numberoffishes,
      ageAtStock: ageAtStock ?? this.ageAtStock,
      isSynced: isSynced ?? this.isSynced,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  factory BatchModel.fromJson(Map<String, dynamic> json) {
    return BatchModel(
      batchId: json['batchId'],
      farmerId: json['farmerId'],
      batchName: json['batchName'],
      averagebodyweight: json['averagebodyweight'],
      fishtype: json['fishtype'],
      numberoffishes: json['numberoffishes'],
      ageAtStock: json['ageAtStock'],
      records:
          (json['records'] as List<dynamic>?)
              ?.map((r) => UnitRecordModel.fromJson(r))
              .toList() ??
          [],
      isCompleted: json['isCompleted'],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'batchId': batchId,
      'farmerId': farmerId,
      'batchName': batchName,
      'fishtype': fishtype,
      'averagebodyweight': averagebodyweight,
      'numberoffishes': numberoffishes,
      'ageAtStock': ageAtStock,
      'records': records?.map((r) => r.toJson()).toList(),
      'isCompleted': isCompleted,
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

// ======================
// Records
// ======================

class UnitRecordModel {
  final String id;
  final int farmerId;
  final String batchId;
  final String unitId;
  final UnitModel? unit;
  final List<DailyRecordModel>? dailyRecords;
  final List<WeightSamplingModel>? weightSamplings;
  final List<GradingAndSortingModel>? gradingAndSortings;
  final List<HarvestFormModel>? harvests;
  final int? fishleft;
  final int? stocknumber;
  final int? incomingfish;
  final int? mortality;
  final int? movedfishes;
  final String? fishtype;
  final DateTime? stockedon;
  final double? totalfishcost;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  UnitRecordModel({
    required this.id,
    required this.farmerId,
    required this.batchId,
    required this.unitId,
    this.unit,
    this.dailyRecords,
    this.weightSamplings,
    this.gradingAndSortings,
    this.harvests,
    this.stocknumber = 0,
    this.fishleft = 0,
    this.mortality = 0,
    this.movedfishes = 0,
    this.incomingfish = 0,
    this.fishtype,
    this.stockedon,
    this.totalfishcost,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  UnitRecordModel copyWith({
    List<DailyRecordModel>? dailyRecords,
    List<WeightSamplingModel>? weightSamplings,
    List<GradingAndSortingModel>? gradingAndSortings,
    List<HarvestFormModel>? harvests,
    // int? numberoffishes,
    String? fishtype,
    DateTime? stockedon,
    double? totalfishcost,
    int? isSynced,
    int? incomingfish,
    int? fishleft,
    DateTime? updatedAt,
  }) {
    return UnitRecordModel(
      id: id,
      farmerId: farmerId,
      batchId: batchId,
      unitId: unitId,
      unit: unit,
      dailyRecords: dailyRecords ?? this.dailyRecords,
      weightSamplings: weightSamplings ?? this.weightSamplings,
      gradingAndSortings: gradingAndSortings ?? this.gradingAndSortings,
      harvests: harvests ?? this.harvests,
      stocknumber: stocknumber,
      fishleft: fishleft,
      mortality: mortality,
      movedfishes: movedfishes,
      fishtype: fishtype ?? this.fishtype,
      stockedon: stockedon ?? this.stockedon,
      totalfishcost: totalfishcost ?? this.totalfishcost,
      isSynced: isSynced ?? this.isSynced,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      incomingfish: incomingfish ?? this.incomingfish,
    );
  }

  factory UnitRecordModel.fromJson(Map<String, dynamic> json) {
    return UnitRecordModel(
      id: json['id'],
      farmerId: json['farmerId'],
      batchId: json['batchId'],
      unitId: json['unitId'],
      stocknumber: json['stocknumber'],
      movedfishes: json['movedfishes'],
      mortality: json['mortality'],
      fishleft: json['fishleft'],
      fishtype: json['fishtype'],
      incomingfish: json['incomingfish'],
      stockedon: json['stockedon'] != null
          ? DateTime.parse(json['stockedon'])
          : null,
      totalfishcost: json['totalfishcost'],
      unit: json['unit'] != null ? UnitModel.fromJson(json['unit']) : null,
      dailyRecords:
          (json['dailyRecords'] as List<dynamic>?)
              ?.map((d) => DailyRecordModel.fromJson(d))
              .toList() ??
          [],
      weightSamplings:
          (json['weightSamplings'] as List<dynamic>?)
              ?.map((w) => WeightSamplingModel.fromJson(w))
              .toList() ??
          [],
      gradingAndSortings:
          (json['gradingAndSortings'] as List<dynamic>?)
              ?.map((g) => GradingAndSortingModel.fromJson(g))
              .toList() ??
          [],
      harvests:
          (json['harvests'] as List<dynamic>?)
              ?.map((h) => HarvestFormModel.fromJson(h))
              .toList() ??
          [],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'farmerId': farmerId,
      'batchId': batchId,
      'fishleft': fishleft,
      'unitId': unitId,
      'stocknumber': stocknumber,
      'mortality': mortality,
      'movedfishes': movedfishes,
      'incomingfish': incomingfish,
      'fishtype': fishtype,
      'stockedon': stockedon?.toIso8601String(),
      'totalfishcost': totalfishcost,
      'unit': unit?.toJson(),
      'dailyRecords': dailyRecords?.map((d) => d.toJson()).toList(),
      'weightSamplings': weightSamplings?.map((w) => w.toJson()).toList(),
      'gradingAndSortings': gradingAndSortings?.map((g) => g.toJson()).toList(),
      'harvests': harvests?.map((h) => h.toJson()).toList(),
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

// ======================
// Daily Record
// ======================

class DailyRecordModel {
  final String id;
  final String recordId;
  final int farmerId;
  final String batchId;
  final String unitId;
  final DateTime date;
  final String feedName;
  final String feedSize;
  final double feedQuantity;
  final int mortality;
  final double? coins;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  DailyRecordModel({
    required this.id,
    required this.recordId,
    required this.farmerId,
    required this.batchId,
    required this.unitId,
    required this.date,
    required this.feedName,
    required this.feedSize,
    required this.feedQuantity,
    required this.mortality,
    this.coins,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  factory DailyRecordModel.fromJson(Map<String, dynamic> json) {
    return DailyRecordModel(
      id: json['id'],
      recordId: json['recordId'],
      farmerId: json['farmerId'],
      batchId: json['batchId'],
      unitId: json['unitId'],
      date: DateTime.parse(json['date']),
      feedName: json['feedName'],
      feedSize: json['feedSize'],
      feedQuantity: (json['feedQuantity'] as num).toDouble(),
      mortality: json['mortality'],
      coins: json['coins'],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'recordId': recordId,
      'farmerId': farmerId,
      'batchId': batchId,
      'unitId': unitId,
      'date': date.toIso8601String(),
      'feedName': feedName,
      'feedSize': feedSize,
      'feedQuantity': feedQuantity,
      'mortality': mortality,
      'coins': coins,
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

// ======================
// Periodic Records
// ======================

class WeightSamplingModel {
  final String id;
  final String recordId;
  final int farmerId;
  final String batchId;
  final String unitId;
  final String sampleName;
  final DateTime date;
  final int fishNumbers;
  final double totalWeight;
  final int completed;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  WeightSamplingModel({
    required this.id,
    required this.recordId,
    required this.farmerId,
    required this.batchId,
    required this.unitId,
    required this.sampleName,
    required this.date,
    required this.fishNumbers,
    required this.totalWeight,
    required this.completed,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  factory WeightSamplingModel.fromJson(Map<String, dynamic> json) {
    return WeightSamplingModel(
      id: json['id'],
      recordId: json['recordId'],
      farmerId: json['farmerId'],
      batchId: json['batchId'],
      unitId: json['unitId'],
      sampleName: json['sampleName'],
      date: DateTime.parse(json['date']),
      fishNumbers: json['fishNumbers'],
      totalWeight: (json['totalWeight'] as num).toDouble(),
      completed: json['completed'],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'recordId': recordId,
      'farmerId': farmerId,
      'batchId': batchId,
      'unitId': unitId,
      'sampleName': sampleName,
      'date': date.toIso8601String(),
      'fishNumbers': fishNumbers,
      'totalWeight': totalWeight,
      'completed': completed,
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

// ======================
// Grading and Sorting
// ======================

class GradingAndSortingModel {
  final String id;
  final String recordId;
  final int farmerId;
  final String batchId;
  final String unitId;
  final String gradeWith;
  final String sampleName;
  final DateTime date;
  final int gradingPondNumber;
  final int fishNumbers;
  final double totalWeight;
  final int completed;
  final List<Grade> grades;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  GradingAndSortingModel({
    required this.id,
    required this.recordId,
    required this.farmerId,
    required this.batchId,
    required this.unitId,
    required this.gradeWith,
    required this.sampleName,
    required this.date,
    required this.gradingPondNumber,
    required this.fishNumbers,
    required this.totalWeight,
    required this.completed,
    this.grades = const [],
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  factory GradingAndSortingModel.fromJson(Map<String, dynamic> json) {
    return GradingAndSortingModel(
      id: json['id'],
      recordId: json['recordId'],
      farmerId: json['farmerId'],
      batchId: json['batchId'],
      unitId: json['unitId'],
      gradeWith: json['gradeWith'],
      sampleName: json['sampleName'],
      date: DateTime.parse(json['date']),
      gradingPondNumber: json['gradingPondNumber'],
      fishNumbers: json['fishNumbers'],
      totalWeight: (json['totalWeight'] as num).toDouble(),
      completed: json['completed'],
      grades:
          (json['grades'] as List<dynamic>?)
              ?.map((g) => Grade.fromJson(g))
              .toList() ??
          [],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'recordId': recordId,
      'id': id,
      'farmerId': farmerId,
      'batchId': batchId,
      'unitId': unitId,
      'gradeWith': gradeWith,
      'sampleName': sampleName,
      'date': date.toIso8601String(),
      'gradingPondNumber': gradingPondNumber,
      'fishNumbers': fishNumbers,
      'totalWeight': totalWeight,
      'completed': completed,
      'grades': grades.map((g) => g.toJson()).toList(),
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

class Grade {
  final String id;
  final String sortingId;
  final String? destinationBatchId;
  final String? destinationBatchName;
  final String destinationUnitId;
  final String destinationUnitName;
  final double averageFishWeight;
  final int fishTransferred;
  final String sampleName;
  final String recordId;
  final String batchId;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Grade({
    required this.id,
    required this.sortingId,
    this.destinationBatchId,
    this.destinationBatchName,
    required this.destinationUnitId,
    required this.sampleName,
    required this.destinationUnitName,
    required this.averageFishWeight,
    required this.fishTransferred,
    required this.recordId,
    required this.batchId,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
  });

  factory Grade.fromJson(Map<String, dynamic> json) {
    return Grade(
      id: json['id'],
      sortingId: json['sortingId'],
      batchId: json['batchId'],
      sampleName: json['sampleName'] ?? "",
      destinationBatchId: json['destinationBatchId'],
      destinationBatchName: json['destinationBatchName'],
      destinationUnitId: json['destinationUnitId'],
      destinationUnitName: json['destinationUnitName'],
      averageFishWeight: (json['averageFishWeight'] as num).toDouble(),
      fishTransferred: json['fishTransferred'],
      recordId: json['recordId'],
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sortingId': sortingId,
      'batchId': batchId,
      'sampleName': sampleName,
      'destinationBatchId': destinationBatchId,
      'destinationBatchName': destinationBatchName,
      'destinationUnitId': destinationUnitId,
      'destinationUnitName': destinationUnitName,
      'averageFishWeight': averageFishWeight,
      'fishTransferred': fishTransferred,
      'recordId': recordId,
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}

// ======================
// Harvest
// ======================
class HarvestFormModel {
  final String id;
  final String recordId;
  final int farmerId;
  final String batchId;
  final String unitId;
  final DateTime date;
  final int isSynced;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String salesInvoiceNumber;
  final int quantityHarvest;
  final double totalWeight;
  final double pricePerKg;
  final double totalSales;

  HarvestFormModel({
    required this.id,
    required this.recordId,
    required this.farmerId,
    required this.batchId,
    required this.unitId,
    required this.date,
    this.isSynced = 0,
    required this.createdAt,
    this.updatedAt,
    required this.salesInvoiceNumber,
    required this.quantityHarvest,
    required this.totalWeight,
    required this.pricePerKg,
    required this.totalSales,
  });

  factory HarvestFormModel.fromJson(Map<String, dynamic> json) {
    return HarvestFormModel(
      id: json['id'],
      recordId: json['recordId'],
      farmerId: json['farmerId'],
      batchId: json['batchId'],
      unitId: json['unitId'],
      date: DateTime.parse(json['date']),
      isSynced: json['isSynced'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
      salesInvoiceNumber: json['salesInvoiceNumber'] ?? '',
      quantityHarvest: json['quantityHarvest'] ?? 0,
      totalWeight: (json['totalWeight'] ?? 0).toDouble(),
      pricePerKg: (json['pricePerKg'] ?? 0).toDouble(),
      totalSales: (json['totalSales'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'recordId': recordId,
      'farmerId': farmerId,
      'batchId': batchId,
      'unitId': unitId,
      'date': date.toIso8601String(),
      'isSynced': isSynced,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'salesInvoiceNumber': salesInvoiceNumber,
      'quantityHarvest': quantityHarvest,
      'totalWeight': totalWeight,
      'pricePerKg': pricePerKg,
      'totalSales': totalSales,
    };
  }
}


class UnitModel {
  final String id; // pondId
  final int farmerId;
  final String unitName;
  final String unitType; // e.g., Earthen, Concrete
  final String unitDimension;
  final int unitCapacity;
  final int fishes; // number of fishes stocked at start
  final String? imageUrl;
  final String imageFile;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String unitcategory; // e.g., "Cage" or "Pond"
  final int isActive; // true if currently in an active batch
  final int isSynced;

  UnitModel({
    required this.id,
    required this.farmerId,
    required this.unitName,
    required this.unitType,
    required this.unitDimension,
    required this.unitCapacity,
    required this.fishes,
    required this.imageFile,
    this.imageUrl,
    required this.createdAt,
    this.updatedAt,
    required this.unitcategory,
    this.isActive = 0,
    this.isSynced = 0,
  });

  factory UnitModel.fromJson(Map<String, dynamic> json) {
    return UnitModel(
      id: json['id'],
      farmerId: json['farmerId'],
      unitName: json['unitName'],
      unitDimension: json['unitDimension'],
      unitType: json['unitType'],
      unitCapacity: json['unitCapacity'],
      fishes: json['fishes'],
      imageFile: json['imageFile'],
      imageUrl: json['imageUrl'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'])
          : null,
      unitcategory: json['unitcategory'],
      isActive: json['isActive'] ?? false,
      isSynced: json['isSynced'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'farmerId': farmerId,
      'unitName': unitName,
      'unitType': unitType,
      'unitDimension': unitDimension,
      'unitCapacity': unitCapacity,
      'fishes': fishes,
      'imageFile': imageFile,
      'imageUrl': imageUrl,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'unitcategory': unitcategory,
      'isActive': isActive,
      'isSynced': isSynced,
    };
  }
}




class IncomeModel {
  final String title;
  final String content;
  final String icon;
  final String id;
  final int farmerId;
  final String pondId;
  final String batchId;
  final String incomeType;
  final double amountEarned;
  final double amount;
  final int quantitySold;
  final String paymentMethod;
  final DateTime incomeDate;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  IncomeModel({
    this.title = "Income",
    required this.id,
    required this.icon,
    required this.content,
    required this.amount,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.incomeType,
    required this.amountEarned,
    required this.quantitySold,
    required this.paymentMethod,
    required this.incomeDate,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class StockingModel {
  final String title;
  final double amount;
  final String icon;
  final String content;
  final String id;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String fishType;
  final int quantityPurchased;
  final double totalAmount;
  final DateTime date;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  StockingModel({
    this.title = "Stocking",
    required this.id,
    required this.amount,
    required this.icon,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.fishType,
    required this.quantityPurchased,
    required this.totalAmount,
    required this.date,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class FeedModel {
  final String id;
  final String title;
  final String icon;
  final String content;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String feedName;
  final String feedForm;
  final String feedSize;
  final int quantity;
  final String unit;
  final double costPerUnit;
  final double totalAmount;
  final DateTime date;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  FeedModel({
    this.title = "Feed",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.feedName,
    required this.feedForm,
    required this.feedSize,
    required this.quantity,
    required this.unit,
    required this.costPerUnit,
    required this.totalAmount,
    required this.date,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class LabourModel {
  final String title;
  final String id;
  final String content;
  final String icon;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String labourType;
  final int numberOfWorkers;
  final double totalAmount;
  final DateTime date;
  final String paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  LabourModel({
    this.title = "Salary/wages",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.labourType,
    required this.numberOfWorkers,
    required this.totalAmount,
    required this.date,
    required this.paymentMethod,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class MedicationModel {
  final String title;
  final String id;
  final String icon;
  final String content;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String medicationName;
  final String quantity;
  final double totalCost;
  final DateTime datePaid;
  final String paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  MedicationModel({
    this.title = "Medications",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.medicationName,
    required this.quantity,
    required this.totalCost,
    required this.datePaid,
    required this.paymentMethod,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class MaintenanceModel {
  final String title;
  final String id;
  final String content;
  final String icon;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String activityType;
  final double totalCost;
  final DateTime datePaid;
  final String paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  MaintenanceModel({
    this.title = "Farm Maintenance",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.activityType,
    required this.totalCost,
    required this.datePaid,
    required this.paymentMethod,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class LogisticsModel {
  final String title;
  final String id;
  final String icon;
  final String content;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String activityType;
  final double totalCost;
  final DateTime datePaid;
  final String paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  LogisticsModel({
    this.title = "Logistics",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.activityType,
    required this.totalCost,
    required this.datePaid,
    required this.paymentMethod,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}

class OperationalExpenseModel {
  final String title;
  final String id;
  final String icon;
  final String content;
  final double amount;
  final int farmerId;
  final String pondId;
  final String batchId; // NEW
  final String expenseName;
  final double totalCost;
  final DateTime datePaid;
  final String paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final int isSynced;

  OperationalExpenseModel({
    this.title = "Other Operations",
    required this.id,
    required this.icon,
    required this.amount,
    required this.content,
    required this.farmerId,
    required this.pondId,
    required this.batchId,
    required this.expenseName,
    required this.totalCost,
    required this.datePaid,
    required this.paymentMethod,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.isSynced = 0,
  });
}