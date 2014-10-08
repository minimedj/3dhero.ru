# -*- coding: utf-8 -*-

from flaskext import wtf
from apps.product.models import Category, Series, Brand


class CategoryForm(wtf.Form):
    name = wtf.TextField(
        u'Название',
        description=u'Введите назнание категории',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичная?',
        default=True,
        description=u'Показывать категорию на сайте?',
        validators=[wtf.validators.optional()]
    )

    def validate(self, is_edit=False):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        name = self.name.data.lower()
        check_cat = Category.query(Category.name_lowercase == name).count()
        if check_cat and not is_edit:
            self.name.errors.append(u'Название категории должно быть уникальным')
            return False
        return True


class SeriesForm(wtf.Form):
    name = wtf.TextField(
        u'Название',
        description=u'Введите назнание серии',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичная?',
        default=True,
        description=u'Показывать серию на сайте?',
        validators=[wtf.validators.optional()]
    )

    def validate(self, is_edit=False):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        name = self.name.data.lower()
        check_cat = Series.query(Series.name_lowercase == name).count()
        if check_cat and not is_edit:
            self.name.errors.append(u'Название серии должно быть уникальным')
            return False
        return True

class BrandForm(wtf.Form):
    name = wtf.TextField(
        u'Название',
        description=u'Введите назнание бренда',
        validators=[wtf.validators.required()]
    )
    is_public = wtf.BooleanField(
        u'Публичный?',
        default=True,
        description=u'Показывать бренд на сайте?',
        validators=[wtf.validators.optional()]
    )

    def validate(self, is_edit=False):
        rv = wtf.Form.validate(self)
        if not rv:
            return False
        name = self.name.data.lower()
        check_cat = Brand.query(Series.name_lowercase == name).count()
        if check_cat and not is_edit:
            self.name.errors.append(u'Название бренда должно быть уникальным')
            return False
        return True

class ProductForm(wtf.Form):
    id_1c = wtf.TextField(
        u'Код 1С',
        description=u'Введите код из базы 1C. Это поле обязательно для заполнения',
        validators=[wtf.validators.required()])
    name = wtf.TextField(
        u'Название',
        description=u'Введите название продукта. Это поле обязательно для заполнения',
        validators=[wtf.validators.required()]
    )
    catalogue_id = wtf.TextField(
        u'Артикул',
        description=u'Введите артикул продукта',
        validators=[wtf.validators.optional()]
    )
    barcode = wtf.TextField(
        u'Штирих-код',
        description=u'Введите штрих-код продукта',
        validators=[wtf.validators.optional()]
    )
    category = wtf.TextField(
        u'Категория',
        description=u'Введите категорию продукта',
        validators=[wtf.validators.optional()]
    )
    brand = wtf.TextField(
        u'Бренд',
        description=u'Введите бренд продукта',
        validators=[wtf.validators.optional()]
    )
    country = wtf.TextField(
        u'Страна',
        description=u'Введите страну-производитель',
        validators=[wtf.validators.optional()]
    )
    rating = wtf.IntegerField(
        u'Рейтинг',
        default=0,
        description=u'Введите рейтинг продукта. '
                    u'Продукты с более высоким рейтингом показываются первыми.',
        validators=[wtf.validators.optional()]
    )
    is_public = wtf.BooleanField(
        u'Видимый?',
        description=u'Показывать продукт на сайте?',
        validators=[wtf.validators.optional()]
    )
    material = wtf.TextField(
        u'Материал',
        description=u'Введите материал продукта. Например: пастик, чугун.',
        validators=[wtf.validators.optional()]
    )
    size = wtf.TextField(
        u'Размер',
        description=u'Введите размер продукта. Например: 10см, 1м.',
        validators=[wtf.validators.optional()]
    )
    weight = wtf.TextField(
        u'Вес',
        description=u'Введите вес продукта. Например: 0.5кг, 2.1т.',
        validators=[wtf.validators.optional()]
    )
    box_material = wtf.TextField(
        u'Материал упаковки',
        description=u'Введите материал упаковки',
        validators=[wtf.validators.optional()]
    )
    box_size = wtf.TextField(
        u'Размер упаковки',
        description=u'Введите размер упаковки',
        validators=[wtf.validators.optional()]
    )
    box_weight = wtf.TextField(
        u'Вес упаковки',
        description=u'Введите вес упаковки',
        validators=[wtf.validators.optional()]
    )
    box_amount = wtf.TextField(
        u'Кол-во в упаковке',
        description=u'Введите кол-во товара в упаковке',
        validators=[wtf.validators.optional()]
    )
    price_retail = wtf.FloatField(
        u'Цена розничная',
        description=u'Введите РРЦ продукта. '
        u'Это поле должно содержать только число, например: "101.50", "50.0"',
        validators=[wtf.validators.optional()]
    )
    price_trade = wtf.FloatField(
        u'Цена оптовая',
        description=u'Введите оптовую цену продукта. '
        u'Это поле должно содержать только число, например: "101.50", "50.0"',
        validators=[wtf.validators.optional()]
    )
    leftovers = wtf.IntegerField(
        u'Остаток',
        description=u'Введите остаток продукта на складе. '
        u'Это поле должно содержать только целое число, например: "14", "1002"',
        validators=[wtf.validators.optional()]
    )
    leftovers_on_way = wtf.IntegerField(
        u'В пути',
        description=u'Введите кол-во товара в пути. '
        u'Это поле должно содержать только целое число, например: "14", "1002"',
        validators=[wtf.validators.optional()]
    )
    receipt_date = wtf.DateField(
        u'Дата поступления',
        description=u'Введите ожидаемую дату поступления на склад (ГГГГ-ММ-ДД)',
        format='%Y-%m-%d',
        validators=[wtf.validators.optional()]
    )
    badge = wtf.TextField(
        u'Бэйдж',
        description=u'Введите текст бейджика, '
                    u'который будет отображать в каталоге рядом с фото товара',
        validators=[wtf.validators.optional()]
    )
    description = wtf.TextAreaField(
        u'Описание',
        description=u'Введите описание товара',
        validators=[wtf.validators.optional()]
    )
    equipment = wtf.TextAreaField(
        u'Комплектация',
        description=u'Введите комплектацию товара',
        validators=[wtf.validators.optional()]
    )
    to_sync = wtf.BooleanField(
        u'Синхронизировать?',
        description=u'Синхронизировать с 5studio?',
        validators=[wtf.validators.optional()]
    )


class AddImageForm(wtf.Form):
    image = wtf.FileField(
        u'Изображение',
        description=u'Выберите изображение для загрузки'
    )
